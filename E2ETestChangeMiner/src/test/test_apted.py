import unittest
import tree_sitter_java
from tree_sitter import Language

from  E2ETestChangeMiner.src.parser.apted.apted_module import tree_to_tree_node, algo_apted, print_distance
from  E2ETestChangeMiner.src.parser.tree_sitter_parser import TreeSitterParser

import re


class TestTreeSitterParser(unittest.TestCase):
    SELENIUM_COMMANDS_REGEX = r"By"
    JUNIT_ANNOTATION_REGEX = r'@(Test|Before|After|BeforeClass|AfterClass|BeforeEach|AfterEach|TestInstance|EnabledIf|DisabledIf|ParameterizedTest|ValueSource|CsvSource)'
    JAVA_LANGUAGE = Language(tree_sitter_java.language())

    def setUp(self):
        self.parser = TreeSitterParser(self.JAVA_LANGUAGE)
        self.parser2 = TreeSitterParser(self.JAVA_LANGUAGE)
        self.old = """Assert.assertTrue(ExpectedConditions.textToBePresentInElement(By.id("test:valueOutput"), "23323232323232").apply(driver));"""
        self.new = """Assert.assertTrue(ExpectedConditions.textToBePresentInElement(By.id("test:valueOutput"), "23323232323232").apply(driver));"""

    def extract_selectors_and_selectors_value_and_content(self, string: str, selector_regex):
        """
        Extracts Selenium selectors, their values, and the remaining tokens from the string.
        """
        selectors = None

        for match in re.finditer(selector_regex, string):
            selectors = match.group(0)  # Type of selector

        stripped_string = re.sub(selector_regex, "", string)

        return selectors, stripped_string

    def test_strings_adpted(self):
        tree1 = self.parser.parse(self.old)
        tree2 = self.parser.parse(self.new)

        node_text1 = self.parser.extract_text_from_node(tree1.root_node, self.parser.get_byte(self.old))
        selectors1, stripped_string1 = self.extract_selectors_and_selectors_value_and_content(
            node_text1, selector_regex=r'\bBy\.[a-zA-Z]+\(.*?\)'
        )

        node_text2 = self.parser.extract_text_from_node(tree2.root_node, self.parser.get_byte(self.new))
        selectors2, stripped_string2 = self.extract_selectors_and_selectors_value_and_content(
            node_text2, selector_regex=r'\bBy\.[a-zA-Z]+\(.*?\)'
        )

        # Check to see if both have a selector; otherwise, skip analysis
        if ((selectors1 is None or selectors2 is None) or (not selectors1 and not selectors2)):
            return

        tree1 = self.parser.parse(stripped_string1)
        tree2 = self.parser.parse(stripped_string2)

        # Convert to TreeNode
        if len(tree1.root_node.children) > 0 and len(tree1.root_node.children[0].children) > 0:
            root1 = tree_to_tree_node(self.parser, tree1.root_node, self.parser.get_byte(stripped_string1))
        else:
            print("Error: the root node of tree1 has no valid children.")
            return

        if len(tree2.root_node.children) > 0 and len(tree2.root_node.children[0].children) > 0:
            root2 = tree_to_tree_node(self.parser, tree2.root_node, self.parser.get_byte(stripped_string2))
        else:
            print("Error: the root node of tree2 has no valid children.")
            return

        # Compute edit distance
        distance, mapping = algo_apted(root1, root2, 0.2, 0.3, 0.4)

        print(f"Edit Mapping:")
        print_distance(distance, mapping)
        print("Selector analysis")

        if distance == 0:
            print(f"Selector comparison: {selectors1} vs {selectors2}")

            # Analyze each selector
            tree1 = self.parser.parse(selectors1)
            tree2 = self.parser.parse(selectors2)

            # Convert to TreeNode
            root1 = tree_to_tree_node(self.parser, tree1.root_node, self.parser.get_byte(selectors1))
            root2 = tree_to_tree_node(self.parser, tree2.root_node, self.parser.get_byte(selectors2))

            # Compute edit distance
            distance, mapping = algo_apted(root1, root2, 0.2, 0.3, 0.4)

            print_distance(distance, mapping)


if __name__ == "__main__":
    unittest.main()
