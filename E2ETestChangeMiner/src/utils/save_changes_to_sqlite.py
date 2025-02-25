import re
from  E2ETestChangeMiner.src.database.database import Database
from  E2ETestChangeMiner.src.parser.tree_sitter_parser import TreeSitterParser
from  E2ETestChangeMiner.src.utils.generate_file_csv_tree import apted_tree_distance, ensure_output_dir


def split_diff(diff_list: list[str]) -> tuple[list[str], list[str]]:
    """
    Splits the differences into two lists: one for deletions (prefix '-') and one for additions (prefix '+').
    """
    removed = [line[1:].strip() for line in diff_list if line.startswith('-')]
    added = [line[1:].strip() for line in diff_list if line.startswith('+')]
    return removed, added

def extract_selectors_and_content(string: str, selector_regex: str):
    """
    Extracts , their values, and the remaining tokens from the string.
    """
    matches = []
    s = re.sub(r'\s+', '', string).strip()
    for match in re.finditer(selector_regex, s):
        matches.append(match.group(0))  # The entire line matching the regex

    stripped_string = re.sub(selector_regex, "", s)
    if not matches:
        return None, stripped_string

    return matches, stripped_string


def are_similar(removed:str, added:str, regex_selector: str, array_support,parser:TreeSitterParser):
    """
    Compares two strings by separately considering  selectors and content.

    """
    selectors1, contents1 = extract_selectors_and_content(removed, regex_selector)
    selectors2,  contents2 = extract_selectors_and_content(added, regex_selector)
    if not selectors1 and not selectors2:
        return False
    distance = apted_tree_distance(contents1, contents2, parser)
    if distance==0:
        # if isinstance(selectors1, list) and isinstance(selectors2, list):
            for s1, s2 in zip(selectors1, selectors2):
                distance = apted_tree_distance(s1, s2, parser)
                array_support.append({
                            "distance": distance,
                            "removed": removed,
                            "added": added,
                            "before_selector": selectors1,
                            "after_selector": selectors2
                        })
        # else:
        #     distance = apted_tree_distance(selectors1, selectors2, parser)
        #     array_support.append({
        #             "distance": distance,
        #             "removed": removed,
        #             "added": added,
        #             "before_selector":selectors1,
        #             "after_selector":selectors2
        #         })
    return array_support


def write_method_deltas_none_changes(commit_id: str, commit_date: str, file_edited: str, file_edit_type: str,
                                     commit_title: str, full_message: str, delta: str,
                                     method_deltas_added: dict[str, str | None],
                                     method_deltas_deleted: dict[str, str | None],
                                     method_deltas_modified: dict[str, str | None],
                                     method_deltas_renamed: dict[str, str | None], conn, project_name: str) -> None:
    if not (method_deltas_added or method_deltas_deleted or method_deltas_modified or method_deltas_renamed):
        conn.insert_change( {
            "repository_name": project_name,
            "Commit ID": commit_id,
            "Commit Date": commit_date,
            "Commit Title": commit_title,
            "Full Message": full_message,
            "Delta": delta,
            "Modified File": file_edited,
            "File Change Type": file_edit_type,
            "Change Type": "NONE",
            "Method Name": "",
            "Old Name": "",
            "New Name": "",
            "Statement/Assertions Removed": "",
            "Statement/Assertions Added": "",
            "Statement/Assertions Modified": "",
            "Before Selector": "",
            "After Selector": ""
        })


def save_changes_to_sqlite(changes_list: list[dict[str, str | None]], regex_selector: str, parser: TreeSitterParser,connectionDb :Database) -> None:
    if connectionDb is not None:
        for change in changes_list:
            project_name= change["repository_name"]
            commit_id = change['commit_id']
            commit_date = change['commit_date']
            message_info = change['message_info']
            file_edited = change['file']
            file_edit_type = change['change_type']
            commit_title = message_info['commit_title']
            full_message = message_info['full_message']
            delta = message_info['delta']

            write_method_deltas_none_changes(commit_id, commit_date, file_edited, file_edit_type, commit_title, full_message,
                                            delta, change['method_deltas'].get('added', []),
                                            change['method_deltas'].get('deleted', []),
                                            change['method_deltas'].get('modified', []),
                                            change['method_deltas'].get('renamed', []), connectionDb, project_name)
            # Inserisci i dati per i metodi aggiunti
            insert_add_method(change['method_deltas'].get('added', []), commit_date, commit_id, connectionDb, delta,
                            file_edit_type, file_edited, full_message, project_name, commit_title)

            # Inserisci i dati per i metodi eliminati
            insert_deleted_method(change['method_deltas'].get('deleted', []), commit_date, commit_id, connectionDb, delta,
                                    file_edit_type, file_edited, full_message, project_name, commit_title)

            # Inserisci i dati per i metodi modificati
            insert_modified_method(change['method_deltas'].get('modified', []), commit_date, commit_id, connectionDb, delta, file_edit_type, file_edited,
                                    full_message, parser, project_name, regex_selector, commit_title)

            # Inserisci i dati per i metodi rinominati
            insert_renamed_method(change['method_deltas'].get('renamed', []), commit_date, commit_id, connectionDb, delta, file_edit_type, file_edited,
                                    full_message, parser, project_name, regex_selector, commit_title)


def insert_renamed_method(changes, commit_date, commit_id, conn, delta, file_edit_type, file_edited, full_message,
                            parser, project_name, regex_selector,commit_title):
    for method in changes:
        statements_rename_removed, statements_rename_added = split_diff(method.get('statements', []))
        array_support = []
        paired_statements = set()
        for i, removed in enumerate(statements_rename_removed):
            if i in paired_statements:
                continue

            for j, added in enumerate(statements_rename_added):
                if j not in paired_statements:
                    are_similar(removed, added, regex_selector, array_support, parser)

            if array_support:
                min_distance_entry = min(array_support, key=lambda x: x["distance"])
                similar_index = statements_rename_added.index(min_distance_entry["added"])
                conn.insert_change( {
                    "repository_name": project_name,
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": commit_title,
                    "Full Message": full_message,
                    "Delta": delta,
                    "Modified File": file_edited,
                    "File Change Type": file_edit_type,
                    "Change Type": "RENAMED",
                    "Method Name": "",
                    "Old Name": method['old_name'],
                    "New Name": method['new_name'],
                    "Statement/Assertions Removed": min_distance_entry["removed"],
                    "Statement/Assertions Added": min_distance_entry["added"],
                    "Statement/Assertions Modified": "",
                    "Before Selector": ";".join( min_distance_entry["before_selector"]),
                    "After Selector": ";".join( min_distance_entry["after_selector"])
                })
                array_support = []
                paired_statements.add(similar_index)
        for j, statements_added in enumerate(statements_rename_added):
            if j not in paired_statements:
                conn.insert_change( {
                    "repository_name": project_name,
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": commit_title,
                    "Full Message": full_message,
                    "Delta": delta,
                    "Modified File": file_edited,
                    "File Change Type": file_edit_type,
                    "Change Type": "RENAMED",
                    "Method Name": "",
                    "Old Name": method['old_name'],
                    "New Name": method['new_name'],
                    "Statement/Assertions Removed": "",
                    "Statement/Assertions Added": statements_added if statements_added else "",
                    "Statement/Assertions Modified": "",
                    "Before Selector": "",
                    "After Selector": ""
                })
        if not statements_rename_removed and not statements_rename_added:
            conn.insert_change( {
                "repository_name": project_name,
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": commit_title,
                "Full Message": full_message,
                "Delta": delta,
                "Modified File": file_edited,
                "File Change Type": file_edit_type,
                "Change Type": "NONE",
                "Method Name": "",
                "Old Name": method['old_name'],
                "New Name": method['new_name'],
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": "",
                "Before Selector": "",
                "After Selector": ""
            })


def insert_modified_method(changes, commit_date, commit_id, conn, delta, file_edit_type, file_edited, full_message,
                            parser, project_name, regex_selector,commit_title):
    for method in changes:
        array_support = []
        statements_modified_removed, statements_modified_added = split_diff(method.get('statements', []))

        paired_statements = set()
        for i, removed in enumerate(statements_modified_removed):
            if i in paired_statements:
                continue

            for j, added in enumerate(statements_modified_added):
                if j not in paired_statements:
                    are_similar(removed, added, regex_selector, array_support, parser)

            if array_support:
                min_distance_entry = min(array_support, key=lambda x: x["distance"])
                similar_index = statements_modified_added.index(min_distance_entry["added"])
                conn.insert_change( {
                    "repository_name": project_name,
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": commit_title,
                    "Full Message": full_message,
                    "Delta": delta,
                    "Modified File": file_edited,
                    "File Change Type": file_edit_type,
                    "Change Type": "MODIFIED",
                    "Method Name": method['name'],
                    "Old Name": "",
                    "New Name": "",
                    "Statement/Assertions Removed":  min_distance_entry["removed"] if min_distance_entry["removed"] else "",
                    "Statement/Assertions Added": "",
                    "Statement/Assertions Modified": min_distance_entry["added"] if min_distance_entry["added"] else "",
                    "Before Selector": ";".join(min_distance_entry["before_selector"]) if  min_distance_entry["before_selector"] else "",
                    "After Selector": ";".join(min_distance_entry["after_selector"]) if  min_distance_entry["after_selector"] else ""
                })
                array_support = []
                paired_statements.add(similar_index)
        for j, added in enumerate(statements_modified_added):
            if j not in paired_statements:
                conn.insert_change({
                    "repository_name": project_name,
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": commit_title,
                    "Full Message": full_message,
                    "Delta": delta,
                    "Modified File": file_edited,
                    "File Change Type": file_edit_type,
                    "Change Type": "MODIFIED",
                    "Method Name": method['name'],
                    "Old Name": "",
                    "New Name": "",
                    "Statement/Assertions Removed": "",
                    "Statement/Assertions Added": added,
                    "Statement/Assertions Modified": "",
                    "Before Selector": "",
                    "After Selector": ""
                })

        if not statements_modified_removed and not statements_modified_added:
            conn.insert_change( {
                "repository_name": project_name,
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": commit_title,
                "Full Message": full_message,
                "Delta": delta,
                "Modified File": file_edited,
                "File Change Type": file_edit_type,
                "Change Type": "NONE",
                "Method Name": method['name'],
                "Old Name": "",
                "New Name": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": "",
                "Before Selector": "",
                "After Selector": ""
            })


def insert_deleted_method(changes, commit_date, commit_id, conn, delta, file_edit_type, file_edited, full_message,
                          project_name,commit_title):
    for method in changes:
        for assertion in method['statements']:
            conn.insert_change( {
                "repository_name": project_name,
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": commit_title,
                "Full Message": full_message,
                "Delta": delta,
                "Modified File": file_edited,
                "File Change Type": file_edit_type,
                "Change Type": "DELETED",
                "Method Name": method['name'],
                "Old Name": "",
                "New Name": "",
                "Statement/Assertions Removed": assertion,
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": "",
                "Before Selector": "",
                "After Selector": ""
            })


def insert_add_method(changes, commit_date, commit_id, conn, delta, file_edit_type, file_edited, full_message,
                      project_name,commit_title):
    for method in changes:
        for assertions_added in method['statements']:
            conn.insert_change( {

                "repository_name": project_name,
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": commit_title,
                "Full Message": full_message,
                "Delta": delta,
                "Modified File": file_edited,
                "File Change Type": file_edit_type,
                "Change Type": "ADDED",
                "Method Name": method['name'],
                "Old Name": "",
                "New Name": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": assertions_added,
                "Statement/Assertions Modified": "",
                "Before Selector": "",
                "After Selector": ""
            })
        if not method['statements']:
            conn.insert_change( {
                "repository_name": project_name,
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": commit_title,
                "Full Message": full_message,
                "Delta": delta,
                "Modified File": file_edited,
                "File Change Type": file_edit_type,
                "Change Type": "NONE",
                "Method Name": method['name'],
                "Old Name": "",
                "New Name": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": "",
                "Before Selector": "",
                "After Selector": ""
            })

