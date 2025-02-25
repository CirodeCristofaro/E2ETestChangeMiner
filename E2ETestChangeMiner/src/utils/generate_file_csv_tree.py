import csv
import os
import re
from pathlib import Path

from  E2ETestChangeMiner.src.config.configuration import CSV_OUTPUT_DIR
from  E2ETestChangeMiner.src.parser.apted.apted_module import tree_to_tree_node, algo_apted
from  E2ETestChangeMiner.src.parser.tree_sitter_parser import TreeSitterParser

CSV_COLUMNS = [
    "Commit ID", "Commit Date", "Commit Title", "Full Message", "Delta",
    "Modified File", "File Change Type", "Change Type", "Method Name", "Old Name",
    "New Name","Statement/Assertions Removed", "Statement/Assertions Added", "Statement/Assertions Modified",
    "Before Selector", "After Selector"
]


def generate_csv_filename(file_path: str) -> str:
    file_name_with_csv = Path(file_path).with_suffix(".csv").name
    return f"{file_name_with_csv}"


def split_diff(diff_list: list[str]) -> tuple[list[str], list[str]]:
    """
    Splits the differences into two lists: one for deletions (prefix '-') and one for additions (prefix '+').
    """
    removed = [line[1:].strip() for line in diff_list if line.startswith('-')]
    added = [line[1:].strip() for line in diff_list if line.startswith('+')]
    return removed, added


def extract_selectors_and_selectors_value_and_content(string: str, selector_regex: str):
    """
    Extracts , their values, and the remaining tokens from the string.
    """
    matches = []
    for match in re.finditer(selector_regex, string):
        matches.append(match.group(0))  # The entire line matching the regex

    stripped_string = re.sub(selector_regex, "", string)
    if not matches:
        print("No selectors found.")
        return None, stripped_string  # Return None and the remaining string if no matches are found
    return matches[0], stripped_string




def are_similar(removed:str, added:str, regex_selector: str, array_support,parser:TreeSitterParser):
    """
    Compares two strings by separately considering  selectors, their values, and content.

    """
    # Extract selectors, selector values, and tokens
    print(f"removed: {removed}")
    print(f"added: {added}")
    selectors1, contents1 = extract_selectors_and_selectors_value_and_content(removed, regex_selector)
    selectors2,  contents2 = extract_selectors_and_selectors_value_and_content(added, regex_selector)

    print(f"Selectors 1 removed: {selectors1}")
    print(f"Selectors 2 added: {selectors2}")
    if not selectors1 and not selectors2:
        return False

    print(f"Content 1 removed: {contents1}")
    print(f"Content 2 added: {contents2}")
    distance = apted_tree_distance(contents1, contents2, parser)
    if distance==0:
        distance = apted_tree_distance(selectors1, selectors2, parser)
        array_support.append({
                "distance": distance,
                "removed": removed,
                "added": added,
                "selector_before":selectors1,
                "selector_after":selectors2
            })
    return array_support


def apted_tree_distance(contents1:str, contents2:str, parser:TreeSitterParser):
    tree1 = parser.parse(contents1)
    tree2 = parser.parse(contents2)
    root1 = tree_to_tree_node(parser, tree1.root_node,parser.get_byte(contents1))
    root2 = tree_to_tree_node(parser, tree2.root_node, parser.get_byte(contents2))
    distance, mapping = algo_apted(root1, root2, 0.2, 0.3, 0.4)
    #print_distance(distance, mapping)
    return distance


def save_changes_to_csv_ted(changes_list: list[dict[str, str | None]], filename: str, repo_name_cleaned: str,
                            repo_file: str, regex_selector: str, parser:TreeSitterParser) -> None:
    directory = ensure_output_dir(repo_name_cleaned, repo_file)
    file_path = os.path.join(directory, filename)

    with (open(file_path, mode='w', newline='', encoding='utf-8') as file):
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS, delimiter=';')
        writer.writeheader()

        for change in changes_list:
            commit_id = change['commit_id']
            commit_date = change['commit_date']
            message_info = change['message_info']
            file_edited = change['file']
            file_edit_type = change['change_type']
            title = message_info['title']
            full_message = message_info['full_message']
            delta = message_info['delta']
            write_method_deltas_none_changes(writer, commit_id, commit_date, file_edited, file_edit_type, title,
                                            full_message, delta, change['method_deltas'].get('added', []),
                                            change['method_deltas'].get('deleted', []),
                                            change['method_deltas'].get('modified', []),
                                            change['method_deltas'].get('renamed', []))
            # Metodi aggiunti
            write_method_deltas_added(writer, commit_id, commit_date, file_edited, file_edit_type, title, full_message,
                                    delta, change['method_deltas'].get('added', []))
            # Metodi eliminati
            write_method_deltas_deleted(writer, commit_id, commit_date, file_edited, file_edit_type, title,
                                        full_message,
                                        delta, change['method_deltas'].get('deleted', []))

            # Metodi modificati
            write_method_deltas_modified(writer, commit_id, commit_date, file_edited, file_edit_type, title,
                                        full_message,delta, change['method_deltas'].get('modified', []),regex_selector,parser)

            # Metodi rinominati
            write_method_deltas_renamed(writer, commit_id, commit_date, file_edited, file_edit_type, title,
                                        full_message, delta, change['method_deltas'].get('renamed', []),regex_selector,parser)


def ensure_output_dir(repo_name, filename)-> Path:
    """ Ensures the output directory exists for the given repository name and file path. """
    repo_name = repo_name.replace("/", "\\")

    file_segments = filename.replace("/", "\\").split("\\")

    # Takes only the last four segments
    if len(file_segments) > 4:
        last_four_segments = "\\".join(file_segments[-4:])
    else:
        last_four_segments = "\\".join(file_segments)

    last_four_segments_without_extension = os.path.splitext(last_four_segments)[0]

    output_dir = CSV_OUTPUT_DIR + repo_name + "\\" + last_four_segments_without_extension

    # Checks if the directory exists, if not, creates it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    else:
        print(f"Directory already exists: {output_dir}")
    return output_dir


def write_method_deltas_added(writer: csv.writer, commit_id: str, commit_date: str,
                                file_edited: str, file_edit_type: str, title: str, full_message: str, delta: str,
                                method_deltas_added: dict[str, str | None]) -> None:
    for method in method_deltas_added:
        for statements_added in method['statements']:
            writer.writerow({
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": title,
                "Full Message": full_message,
                "Delta": delta,
                "Modified File": file_edited,
                "File Change Type": file_edit_type,
                "Change Type": "ADDED",
                "Method Name": method['name'],
                "Old Name": "",
                "New Name": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": statements_added,
                "Statement/Assertions Modified": "",
            })
        if not method['statements']:
            writer.writerow({
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": title,
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
            })


def write_method_deltas_deleted(writer: csv.writer, commit_id: str, commit_date: str,
                                file_edited: str, file_edit_type: str, title: str, full_message: str, delta: str,
                                method_deltas_deleted: dict[str, str | None]) -> None:
    # Metodi eliminati
    for method in method_deltas_deleted:
        for assertion in method['statements']:
            writer.writerow({
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": title,
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
                "Statement/Assertions Modified": ""
            })


def write_method_deltas_modified(writer: csv.writer, commit_id: str, commit_date: str,
                                file_edited: str, file_edit_type: str, title: str, full_message: str, delta: str,
                                method_deltas_modified: dict[str, str | None], regex_selector: str, parser) -> None:
    array_support = []
    for method in method_deltas_modified:
        assertion_modified_removed, assertion_modified_added = split_diff(method.get('statements', []))

        paired_statements = set()
        for i, removed in enumerate(assertion_modified_removed):
            if i in paired_statements:
                continue

            for j, added in enumerate(assertion_modified_added):
                if j not in paired_statements:
                    are_similar(removed, added, regex_selector, array_support, parser)

            if array_support:
                min_distance_entry = min(array_support, key=lambda x: x["distance"])
                similar_index = assertion_modified_added.index(min_distance_entry["added"])

                writer.writerow({
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": title,
                    "Full Message": full_message,
                    "Delta": delta,
                    "Modified File": file_edited,
                    "File Change Type": file_edit_type,
                    "Change Type": "MODIFIED",
                    "Method Name": method['name'],
                    "Old Name": "",
                    "New Name": "",
                    "Statement/Assertions Removed": min_distance_entry["removed"] if min_distance_entry["removed"] else "",
                    "Statement/Assertions Added": "",
                    "Statement/Assertions Modified": min_distance_entry["added"] if min_distance_entry["added"] else "",
                    "Before Selector": min_distance_entry["selector_before"] if  min_distance_entry["selector_before"] else "",
                    "After Selector": min_distance_entry["selector_after"] if  min_distance_entry["selector_after"] else "",
                })

                paired_statements.add(similar_index)

        # Scrivere le asserzioni aggiunte che non sono state abbinate
        for j, added in enumerate(assertion_modified_added):
            if j not in paired_statements:
                writer.writerow({
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": title,
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
                })

        # Se nessuna modifica,
        if not assertion_modified_removed and not assertion_modified_added:
            writer.writerow({
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": title,
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
            })




def write_method_deltas_renamed(writer: csv.writer, commit_id: str, commit_date: str,
                                file_edited: str, file_edit_type: str, title: str, full_message: str, delta: str,
                                method_deltas_renamed: dict[str, str | None],regex_selector:str,parser) -> None:
    array_support=[]
    for method in method_deltas_renamed:
        assertion_rename_removed, assertion_rename_added = split_diff(method.get('statements', []))

        paired_statements = set()
        for i, removed in enumerate(assertion_rename_removed):
            if i in paired_statements:
                continue

            for j, added in enumerate(assertion_rename_added):
                if j not in paired_statements:
                    are_similar(removed, added, regex_selector, array_support, parser)

            if array_support:
                min_distance_entry = min(array_support, key=lambda x: x["distance"])
                similar_index = assertion_rename_added.index(min_distance_entry["added"])
                writer.writerow({
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": title,
                    "Full Message": full_message,
                    "Delta": delta,
                    "Modified File": file_edited,
                    "File Change Type": file_edit_type,
                    "Change Type": "RENAMED",
                    "Method Name": "",
                    "Old Name": method['old_name'],
                    "New Name": method['new_name'],
                    "Statement/Assertions Removed": min_distance_entry["removed"] if min_distance_entry["removed"] else "",
                    "Statement/Assertions Added": min_distance_entry["added"] if min_distance_entry["added"] else "",
                    "Statement/Assertions Modified": ""
                })
                paired_statements.add(similar_index)


        for j, assertion_added in enumerate(assertion_rename_added):
            if j not in paired_statements:
                writer.writerow({
                    "Commit ID": commit_id,
                    "Commit Date": commit_date,
                    "Commit Title": title,
                    "Full Message": full_message,
                    "Delta": delta,
                    "Modified File": file_edited,
                    "File Change Type": file_edit_type,
                    "Change Type": "RENAMED",
                    "Method Name": "",
                    "Old Name": method['old_name'],
                    "New Name": method['new_name'],
                    "Statement/Assertions Removed": "",
                    "Statement/Assertions Added": assertion_added if assertion_added else "",
                    "Statement/Assertions Modified": ""
                })

        if  not assertion_rename_removed and not assertion_rename_added:
            writer.writerow({
                "Commit ID": commit_id,
                "Commit Date": commit_date,
                "Commit Title": title,
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
                "Statement/Assertions Modified": ""
            })


def write_method_deltas_none_changes(writer: csv.writer, commit_id: str, commit_date: str,
                                    file_edited: str, file_edit_type: str, title: str, full_message: str, delta: str,
                                    method_deltas_added: dict[str, str | None],
                                    method_deltas_deleted: dict[str, str | None],
                                    method_deltas_modified: dict[str, str | None],
                                    method_deltas_renamed: dict[str, str | None]) -> None:
    if not (method_deltas_added or method_deltas_deleted or method_deltas_modified or method_deltas_renamed):
        writer.writerow({
            "Commit ID": commit_id,
            "Commit Date": commit_date,
            "Commit Title": title,
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
            "Statement/Assertions Modified": ""
        })