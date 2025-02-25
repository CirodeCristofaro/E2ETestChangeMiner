from typing import List

from  E2ETestChangeMiner.src.analyzers.abstract.test_framework_analyzer import TestFrameworkAnalyzer


class SeleniumAnalyzer(TestFrameworkAnalyzer):
    """
    Selenium Filter: Checks if a method contains assertions.
    """
    SELENIUM_COMMANDS_REGEX = r"By"
    def __init__(self, parser):
        self.parser=parser
        pass

    def find_assertions_or_statements(self, method_code: str) -> List[str]:
        """
        Finds assertions or Selenium statements in the method code.
        Returns a list of strings representing the reconstructed code blocks found.
        """
        array_support = []  # List to store the nodes
        tree = self.parser.parse(method_code)  # Parse the method code
        # Mark the nodes that match the regex
        self.parser.mark_by_invocations(tree.root_node, self.parser.get_byte(method_code), self.SELENIUM_COMMANDS_REGEX,
                                        array_support)

        # List to store the reconstructed code
        array = []
        for node in array_support:
            # Reconstruct the node's text and add it to the list
            reconstructed_code = self.parser.get_full_line_from_node(node,self.parser.get_byte(method_code))
            array.append(reconstructed_code)

        return array

