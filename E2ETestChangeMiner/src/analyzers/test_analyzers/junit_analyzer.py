from typing import List

from E2ETestChangeMiner.src.analyzers.abstract.test_framework_analyzer import TestFrameworkAnalyzer


class JUnitAnalyzer(TestFrameworkAnalyzer):
    """
    JUnit Filter: Checks if a method is annotated as a JUnit test or contains assertions.
    """
    JUNIT_ANNOTATION_REGEX = r'@(Test|Before|After|BeforeClass|AfterClass|BeforeEach|AfterEach|TestInstance|EnabledIf|DisabledIf|ParameterizedTest|ValueSource|CsvSource)'
    # ASSERTION_REGEX = r'(\w+\.)?(assertEquals|assertTrue|assertFalse|assertThat|assertNull|assertNotNull|assertSame|assertNotSame|assertArrayEquals|assertThrows|assertDoesNotThrow|assertAll)\(([\s\S]*?)\);'

    def __init__(self, parser):
        self.parser = parser
        pass

    def find_annotations(self, method_code: str) -> List[str]:
        """
        Finds the lines that contain JUnit annotations in the method.
        """

        array_support = []  # List to store the nodes
        tree = self.parser.parse(method_code)  # Parse the method code

        # Mark the nodes that match the regex
        self.parser.mark_by_annotations(tree.root_node,self.parser.get_byte(method_code), self.JUNIT_ANNOTATION_REGEX, array_support)

        # List to store the reconstructed code
        array = []
        for node in array_support:
            # Reconstruct the node's text and add it to the list
            reconstructed_code = self.parser.reconstruct_line_or_block(node,self.parser.get_byte(method_code))
            array.append(reconstructed_code)

        return array
    def find_assertions_or_statements(self, method_code: str) -> List[str]:
        """
        Finds the lines that contain JUnit assertions in the method, excluding comments.
        """

        return []
