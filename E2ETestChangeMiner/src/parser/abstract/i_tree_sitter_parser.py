from abc import ABC, abstractmethod

from tree_sitter import Tree

class ITreeSitterParser(ABC):
    @abstractmethod
    def parse(self, source_code: str) -> Tree:
        """Parses the given source code and returns the syntax tree."""
        pass

    @abstractmethod
    def get_byte(self, source_code: str) -> bytes:
        """Converts the source code into bytes."""
        pass

    @abstractmethod
    def reconstruct_line_or_block(self, node, src: bytes) -> str:
        """Reconstructs and extracts the content of a line or block."""
        pass

    @abstractmethod
    def extract_text_from_node(self, node, src: bytes) -> str:
        """Extracts the text content of a syntax tree node."""
        pass

    @abstractmethod
    def mark_by_invocations(self, node, src: bytes, pattern: str, array: list, p=None) -> bool:
        """Marks nodes based on method invocations matching a pattern."""
        pass

    @abstractmethod
    def mark_by_annotations(self, node, node_text: str, pattern: str, array: list) -> bool:
        """Marks nodes based on annotations matching a pattern."""
        pass

    @abstractmethod
    def process_method_invocation(self, node, node_text: str, pattern: str, array: list,program_text:str) -> bool:
        """Processes method invocations and adds matching nodes."""
        pass

    @abstractmethod
    def get_full_line_from_node(self, node, src: bytes) -> str:
        """Retrieves the entire line of source code containing the specified syntax node."""
        pass
