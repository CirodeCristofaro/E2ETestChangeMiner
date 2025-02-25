from abc import ABC, abstractmethod
from typing import List

class TestFrameworkAnalyzer(ABC):
    """
    Abstract class to handle common annotations and assertions in test frameworks.
    """

    def find_annotations(self, method_code: str) -> List[str]:
        """
        Finds the annotations in a method.
        """

        return []

    @abstractmethod
    def find_assertions_or_statements(self, method_code: str) -> List[str]:
        """
        Finds the assertions or statements in a method.
        """
        pass
