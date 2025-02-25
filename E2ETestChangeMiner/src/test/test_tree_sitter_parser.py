import unittest

import tree_sitter_java
from tree_sitter import Language

from  E2ETestChangeMiner.src.parser.tree_sitter_parser import TreeSitterParser


class TestTreeSitterParser(unittest.TestCase):
    SELENIUM_COMMANDS_REGEX = (
        r"By"
    )
    JUNIT_ANNOTATION_REGEX =( r'@(Test|Before|After|BeforeClass|'
                              r'AfterClass|BeforeEach|AfterEach|'
                              r'TestInstance|EnabledIf|DisabledIf|'
                              r'ParameterizedTest|ValueSource|CsvSource)')
    JAVA_LANGUAGE = Language(tree_sitter_java.language())
    def setUp(self):
        self.parser = TreeSitterParser(self.JAVA_LANGUAGE)
        self.src = """
final List<WebElement> h3s =
 m_driver.findElements(By.tagName("h3"));

        """

    def print_tree(self, tree):
        """
        Function to print the details of all nodes in the tree.
        """

        def print_node_details(node, indent=0):
            node_text = self.src[node.start_byte:node.end_byte].strip()
            print(' ' * indent + f" Node type: {node.type}, Node text: {node_text},  Start: {node.start_byte}, End: {node.end_byte}")
            for child in node.children:
                print_node_details(child, indent + 2)

        print("Syntax Tree:")
        print_node_details(tree.root_node)


    def test_reconstruct_line_or_block(self):
        tree = self.parser.parse(self.src)
        array=[]
     #   self.print_tree(tree)
        self.parser.mark_by_invocations(tree.root_node, self.parser.get_byte(self.src), self.SELENIUM_COMMANDS_REGEX,
                                        array)
      #  self.parser.mark_by_annotations(tree.root_node,self.parser.get_byte(self.src), self.JUNIT_ANNOTATION_REGEX,array)
        #print(array)
        for node in array:
         print(self.parser.get_full_line_from_node(node,self.parser.get_byte(self.src)))


if __name__ == "__main__":
    unittest.main()
