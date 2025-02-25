import csv
import os
from difflib import SequenceMatcher
from pathlib import Path
from  E2ETestChangeMiner.src.config.configuration import CSV_OUTPUT_DIR
import re


CSV_COLUMNS = [
    "Commit ID", "Commit Date", "Commit Title", "Full Message", "Delta",
    "Modified File", "File Change Type", "Change Type", "Method Name", "Old Name",
    "New Name", "Annotations Removed", "Annotations Added", "Annotations Modified",
    "Statement/Assertions Removed", "Statement/Assertions Added", "Statement/Assertions Modified",
    "Before Selector","After Selector"
]
def generate_csv_filename( file_path: str) -> str:
    file_name_with_csv = Path(file_path).with_suffix(".csv").name
    return f"{file_name_with_csv}"

def split_diff(diff_list: list[str]) -> tuple[list[str], list[str]]:
    """
    Splits the differences into two lists: one for deletions (prefix '-') and one for additions (prefix '+').
    """
    removed = [line[1:].strip() for line in diff_list if line.startswith('-')]
    added = [line[1:].strip() for line in diff_list if line.startswith('+')]
    return removed, added


def extract_selectors_and_selectors_value_and_content(string: str):
    """
    Extracts Selenium selectors, their content, and the remaining tokens from a string.

    :param string: The string to process.
    :return: A tuple containing (selectors, selector values, remaining content tokens).
    """
    # Regex to find Selenium selectors
    selector_regex = r'\b(?:By\.)?(id|className|name|xpath|cssSelector|linkText|partialLinkText|Id|XPath|tagName|findElement)\((["\'])(.*?)\2\)'

    # Extract selectors and their values
    selectors = []
    selector_values = []

    for match in re.finditer(selector_regex, string):
        selectors.append(match.group(1))  # Selector type
        selector_values.append(match.group(3))  # Value inside the selector

    # Remove selectors from the string
    stripped_string = re.sub(selector_regex, "", string)

    # Tokenize the remaining string
    return selectors, selector_values, stripped_string

def extract_selectors_and_selectors_value(string):
    """
    Extracts Selenium selectors, their content, and the remaining tokens from a string.

    :param string: The string to process.
    :return: A tuple containing (selectors, selector values, remaining content tokens).
    """
    # Regex to find Selenium selectors
    selector_regex = r'\b(?:By\.)?(id|className|name|xpath|cssSelector|linkText|partialLinkText|Id|XPath|tagName|findElement)\((["\'])(.*?)\2\)'

    # Extract selectors and their values
    selectors = [match.group(0) for match in re.finditer(selector_regex, string)]

    return "".join(selectors) if selectors else ""

def jaccard_similarity(set1, set2):
    """
    Computes the Jaccard similarity between two sets.

    :param set1: First set.
    :param set2: Second set.
    :return: Jaccard similarity (float between 0 and 1).
    """
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0

def tokenize_selector_values(selector_values):
    """
    Tokenizes the content of selector values to handle concatenations and variables.

    :param selector_values: List of selector values (e.g., XPath expressions).
    :return: List of tokenized selector values.
    """
    tokenized_values = []
    for value in selector_values:
        # Tokenize based on string components, variables, and operators, and handle special characters in strings correctly
        tokens = re.findall(r"[a-zA-Z0-9]+|_|[\(\)\[\]\.;,=&\"\'/<>:!@#\$%\^\*\+\-\.\{\}]+|\"[^\"]*\"|'[^']*'", value)
        tokenized_values.append(tokens)
    return tokenized_values


def are_similar(str1, str2, threshold=1.79,selector_weight=1,  selector_value_weight=0.5, content_weight=0.5):
    """
    Compares two strings by separately considering Selenium selectors, their values, and content.

    :param str1: First string.
    :param str2: Second string.
    :param threshold: Similarity threshold to consider strings "similar".
    :param selector_value_weight: Weight of selector values in the overall similarity.
    :param content_weight: Weight of content in the overall similarity.
    :param selector_weight: Weight of select in the overall similarity.
    :return: True if the overall similarity exceeds the threshold, False otherwise.
    """
    # Extract selectors, selector values, and tokens
    print(f"str1: {str1}")
    print(f"str2: {str2}")
    selectors1, selector_values1, contents1 = extract_selectors_and_selectors_value_and_content(str1)
    selectors2, selector_values2, contents2 = extract_selectors_and_selectors_value_and_content(str2)

    print(f"Selectors 1: {selectors1}")
    print(f"Selectors 2: {selectors2}")
    print(f"Selector values 1: {selector_values1}")
    print(f"Selector values 2: {selector_values2}")
    print(f"Content 1: {contents1}")
    print(f"Content 2: {contents2}")
    if not selectors1 and not selectors2:
        return False

    tokenized_selector_values1 = tokenize_selector_values(selector_values1)
    tokenized_selector_values2 = tokenize_selector_values(selector_values2)

    print(f"Tokenized selector values 1: {tokenized_selector_values1}")
    print(f"Tokenized selector values 2: {tokenized_selector_values2}")

    # Flatten tokenized values for Jaccard similarity
    flat_tokens1 = {token for tokens in tokenized_selector_values1 for token in tokens}
    flat_tokens2 = {token for tokens in tokenized_selector_values2 for token in tokens}
    # Calculate similarities
    selector_similarity = SequenceMatcher(None, selectors1, selectors2).ratio()
    selector_value_similarity = jaccard_similarity(flat_tokens1, flat_tokens2)
    content_similarity = SequenceMatcher(None, contents1, contents2).ratio()

    print(f"Selector similarity: {selector_similarity}")
    print(f"Selector value similarity: {selector_value_similarity}")
    print(f"Content similarity: {content_similarity}")

    # Calculate the weighted similarity
    weighted_similarity = (
            selector_weight * selector_similarity +
            selector_value_weight * selector_value_similarity +
            content_weight * content_similarity
    )
    print(f"Weighted similarity: {weighted_similarity} (threshold={threshold})")
    return weighted_similarity >= threshold


def save_changes_to_csv(changes_list: list[dict[str, str | None]], filename: str,repo_name_cleaned:str,repo_file:str) -> None:
    directory= ensure_output_dir(repo_name_cleaned,repo_file)
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
                                                full_message, delta, change['method_deltas'].get('added',[]),
                                                change['method_deltas'].get('deleted',[]),
                                                change['method_deltas'].get('modified',[]),
                                                change['method_deltas'].get('renamed', []))
            # Metodi aggiunti
            write_method_deltas_added(writer,commit_id, commit_date, file_edited, file_edit_type, title, full_message,
                                        delta,change['method_deltas'].get('added', []))
            # Metodi eliminati
            write_method_deltas_deleted(writer, commit_id, commit_date, file_edited, file_edit_type, title, full_message,
                                        delta, change['method_deltas'].get('deleted', []))

            # Metodi modificati
            write_method_deltas_modified(writer, commit_id, commit_date, file_edited, file_edit_type, title, full_message,
                                        delta, change['method_deltas'].get('modified', []))

            # Metodi rinominati
            write_method_deltas_renamed(writer, commit_id, commit_date, file_edited, file_edit_type, title,
                                        full_message,delta, change['method_deltas'].get('renamed', []))


def ensure_output_dir(repo_name, filename):
    """ Ensures the output directory exists for the given repository name and file path. """
    repo_name = repo_name.replace("/", "\\")

    file_segments = filename.replace("/", "\\").split("\\")

    # Takes only the last four segments
    if len(file_segments) > 4:
        last_two_segments = "\\".join(file_segments[-4:])
    else:
        last_two_segments = "\\".join(file_segments)

    last_two_segments_without_extension = os.path.splitext(last_two_segments)[0]

    output_dir = CSV_OUTPUT_DIR + repo_name + "\\" + last_two_segments_without_extension

    # Checks if the directory exists, if not, creates it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    else:
        print(f"Directory already exists: {output_dir}")
    return output_dir

def write_method_deltas_added(writer: csv.writer, commit_id: str, commit_date: str,
                                    file_edited: str, file_edit_type: str,title:str,full_message:str,delta:str, method_deltas_added:  dict[str, str | None]) -> None:
    for method in method_deltas_added:
        for statements_added in method['annotations']:
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
                "Annotations Removed": "",
                "Annotations Added": statements_added,
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": "",
            })
        for assertions_added in method['statements']:
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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": assertions_added,
                "Statement/Assertions Modified": "",
            })
        if not (method['statements'] and method['annotations']):
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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": "",
            })

def write_method_deltas_deleted(writer: csv.writer, commit_id: str, commit_date: str,
                                    file_edited: str, file_edit_type: str,title:str,full_message:str,delta:str, method_deltas_deleted:  dict[str, str | None]) -> None:
    # Metodi eliminati
    for method in method_deltas_deleted:
        for annotation in method['annotations']:
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
                "Annotations Removed": annotation,
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": ""
            })
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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": assertion,
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": ""
            })


def write_method_deltas_modified(writer: csv.writer, commit_id: str, commit_date: str,
                                    file_edited: str, file_edit_type: str,title:str,full_message:str,delta:str, method_deltas_modified:  dict[str, str | None]) -> None:
    for method in  method_deltas_modified:
        annotation_modified_removed, annotation_modified_added = split_diff(method.get('annotations', []))
        assertion_modified_removed, assertion_modified_added = split_diff(method.get('statements', []))

        paired_assertions = set()
        for i, removed in enumerate(assertion_modified_removed):
            if i in paired_assertions:
                continue

            similar_index = -1
            for j, added in enumerate(assertion_modified_added):
                if j not in paired_assertions and are_similar(removed, added):
                    similar_index = j
                    break


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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": removed if removed else "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": assertion_modified_added[
                    similar_index] if similar_index != -1 else "",
                "Before Selector": extract_selectors_and_selectors_value(removed) if removed and similar_index != -1 else "",
                "After Selector": extract_selectors_and_selectors_value(assertion_modified_added[
                    similar_index]) if similar_index != -1 and removed   else ""
            })

            if similar_index != -1:
                paired_assertions.add(similar_index)


        for j, added in enumerate(assertion_modified_added):
            if j not in paired_assertions:
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
                    "Annotations Removed": "",
                    "Annotations Added": "",
                    "Annotations Modified": "",
                    "Statement/Assertions Removed": "",
                    "Statement/Assertions Added": added,
                    "Statement/Assertions Modified": ""
                })

        for annotation in annotation_modified_removed:
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
                "Annotations Removed": annotation,
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": ""
            })
        for assertion in annotation_modified_added:
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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": assertion
            })

        # Se nessuna modifica,
        if not annotation_modified_removed and not annotation_modified_added and not assertion_modified_removed and not assertion_modified_added:
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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": ""
            })



def write_method_deltas_renamed(writer: csv.writer, commit_id: str, commit_date: str,
                                    file_edited: str, file_edit_type: str,title:str,full_message:str,delta:str, method_deltas_renamed:  dict[str, str | None]) -> None:
    for method in method_deltas_renamed:
        annotation_rename_removed, annotation_rename_added = split_diff(method.get('annotations', []))
        assertion_rename_removed, assertion_rename_added = split_diff(method.get('statements', []))


        paired_assertions = set()

        for annotation in annotation_rename_added:
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
                "Annotations Removed": "",
                "Annotations Added": annotation,
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": ""
            })
        for annotation in assertion_rename_removed:
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
                "Annotations Removed": annotation,
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": ""
            })

        for i, assertion_removed in enumerate(assertion_rename_removed):
            similar_assertion_index = -1
            for j, assertion_added in enumerate(assertion_rename_added):
                if j not in paired_assertions and are_similar(assertion_removed, assertion_added):
                    similar_assertion_index = j
                    break

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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": assertion_removed if assertion_removed else "",
                "Statement/Assertions Added": assertion_rename_added[
                    similar_assertion_index] if similar_assertion_index != -1 else "",
                "Statement/Assertions Modified": ""
            })


            if similar_assertion_index != -1:
                paired_assertions.add(similar_assertion_index)

        for j, assertion_added in enumerate(assertion_rename_added):
            if j not in paired_assertions:
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
                    "Annotations Removed": "",
                    "Annotations Added": "",
                    "Annotations Modified": "",
                    "Statement/Assertions Removed": "",
                    "Statement/Assertions Added": assertion_added if assertion_added else "",
                    "Statement/Assertions Modified": ""
                })


        if not annotation_rename_removed and not annotation_rename_added and not assertion_rename_removed and not assertion_rename_added:
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
                "Annotations Removed": "",
                "Annotations Added": "",
                "Annotations Modified": "",
                "Statement/Assertions Removed": "",
                "Statement/Assertions Added": "",
                "Statement/Assertions Modified": ""
            })

def write_method_deltas_none_changes(writer: csv.writer, commit_id: str, commit_date: str,
                                    file_edited: str, file_edit_type: str,title:str,full_message:str,delta:str,method_deltas_added:  dict[str, str | None], method_deltas_deleted:  dict[str, str | None],
                                    method_deltas_modified: dict[str, str | None],method_deltas_renamed:  dict[str, str | None]) -> None:
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
            "Annotations Removed": "",
            "Annotations Added": "",
            "Annotations Modified": "",
            "Statement/Assertions Removed": "",
            "Statement/Assertions Added": "",
            "Statement/Assertions Modified": ""
        })