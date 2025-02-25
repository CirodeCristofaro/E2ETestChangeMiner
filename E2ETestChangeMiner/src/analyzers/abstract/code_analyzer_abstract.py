from abc import ABC, abstractmethod

from pydriller import ModifiedFile


class CodeAnalyzerAbstract(ABC):
    @abstractmethod
    def extract_method_code(self, source_code: str, start_line: int, end_line: int) -> str:
        """Extracts the method code based on the starting and ending lines."""
        pass

    @abstractmethod
    def analyze_methods(self, mod: ModifiedFile)-> dict[str, list]:
        """Analyzes the methods in a file."""
        pass