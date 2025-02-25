import re

from tree_sitter import Parser, Tree

from E2ETestChangeMiner.src.parser.abstract.i_tree_sitter_parser import ITreeSitterParser


class TreeSitterParser(ITreeSitterParser):
    def __init__(self, language_path):
        """
        Initializes the TreeSitterParser.
        :param language_path: Path to the language grammar file for Tree-sitter.
        """
        self.parser = Parser(language_path)

    def parse(self, source_code: str) -> Tree:
        """
        Parses the given source code using Tree-sitter.
        :param source_code: The source code to parse.
        :return: The parsed syntax tree.
        """
        src = self.get_byte(source_code)
        return self.parser.parse(src)

    def get_byte(self, source_code):
        src = bytes(source_code, "utf-8")
        return src

    def reconstruct_line_or_block(self, node, src: bytes) -> str:
        """
        Reconstructs and extracts the content of a line or block from the source code.
        :param node: The syntax tree node representing the line/block.
        :param src: The source code as bytes.
        :return: The reconstructed text without whitespace.
        """
        start_byte = node.start_byte
        end_byte = node.end_byte
        block = src[start_byte:end_byte + 1].decode('utf-8')
        return ''.join(block.split())

    def extract_text_from_node(self, node, src: bytes) -> str:
        """
        Extracts the text content of a syntax tree node.
        :param node: The syntax tree node.
        :param src: The source code as bytes.
        :return: The extracted and trimmed text.
        """
        return re.sub(r'\s+', '', src[node.start_byte:node.end_byte].decode('utf-8')).strip()

    def mark_by_invocations(self, node, src: bytes, pattern: str, array: list, program_line=None) -> bool:
        """
        Marks nodes that match a pattern in comments or method invocations.
        :param node: The syntax tree node to check.
        :param src: The source code as bytes.
        :param pattern: The regular expression pattern to match.
        :param array: A list to store nodes.
        :param program_line: The program line to check.
        :return: True if a matching node is found; otherwise, False.
        """
        # Save the initial state of the array for potential rollback
        initial_length = len(array)

        # If the node is of type 'expression_statement' or 'local_variable_declaration',
        # save its byte offset and text
        if (node.type == "expression_statement" or node.type == "local_variable_declaration"
                or node.type == "return_statement"):
            program_text = self.extract_text_from_node(node, src)

            array.append({
                'type': node.type,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'text': program_text
            })

        # If the node is an identifier, apply the regex
        if node.type == "identifier":
            node_text = self.extract_text_from_node(node, src)
            if self.process_method_invocation(node, node_text, pattern, array, program_line):
                return True  # Node found and added

        # Iterate through the children
        found_in_child = False
        for child in node.children:
            if self.mark_by_invocations(child, src, pattern, array, program_line):
                found_in_child = True

        # If no child satisfies the condition, rollback the array
        if not found_in_child:
            # Restore the array to its initial state
            del array[initial_length:]

        return found_in_child

    def mark_by_annotations(self, node, src: bytes, pattern: str, array: list) -> bool:
        """
        Marks nodes based on annotations that match a pattern.
        :param node: The syntax tree node to check.
        :param src: The source code as bytes.
        :param pattern: The regular expression pattern to match.
        :param array: A list to store nodes.
        :return: True if a matching annotation is found; otherwise, False.
        """
        if node.type == "marker_annotation":
            node_text = self.extract_text_from_node(node, src)
            if re.search(pattern, node_text):
                array.append(node)
                return True
        found_in_child = False

        for child in node.children:
            if self.mark_by_annotations(child, src, pattern, array):
                found_in_child = True

        return found_in_child


    def process_method_invocation(self, node, node_text: str, pattern: str, array: list,program_text:str) -> bool:
        """
        Processes method invocations and adds the node if it matches the pattern.
        :param node: The syntax tree node representing the method invocation.
        :param node_text: The source code as bytes.
        :param pattern: The regular expression pattern to match.
        :param array: A list to store nodes.
        :param program_text:
        :return: True if the node is equal to the pattern; otherwise, False.
        """
        if node_text == pattern:
            return True
        return False

    def get_full_line_from_node(self, node, src: bytes) -> str:
        """
        Retrieves the entire line of source code containing the specified syntax node.
        :param node: The syntax node from which to extract the line.
        :param src: The source code as bytes.
        :return: The complete line of source code as a string.
        """
        return src[node['start_byte']:node['end_byte']].decode('utf-8').strip()

