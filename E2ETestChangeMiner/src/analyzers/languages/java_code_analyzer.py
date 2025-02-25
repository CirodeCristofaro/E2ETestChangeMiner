import difflib
from typing import List, Dict, Any
import tree_sitter_java
from tree_sitter import Language
from  E2ETestChangeMiner.src.parser.tree_sitter_parser import TreeSitterParser
from  E2ETestChangeMiner.src.analyzers.abstract.code_analyzer_abstract import CodeAnalyzerAbstract
from  E2ETestChangeMiner.src.analyzers.abstract.test_framework_analyzer import TestFrameworkAnalyzer
from  E2ETestChangeMiner.src.analyzers.test_analyzers.junit_analyzer import JUnitAnalyzer
from  E2ETestChangeMiner.src.analyzers.test_analyzers.selenium_analyzer import SeleniumAnalyzer


class JavaCodeAnalyzer(CodeAnalyzerAbstract):

    JAVA_PARSER_LANGUAGE = Language(tree_sitter_java.language())
    parser = TreeSitterParser(JAVA_PARSER_LANGUAGE)

    def __init__(self):
        self.filters: List[TestFrameworkAnalyzer] = [
            JUnitAnalyzer(self.parser),
            SeleniumAnalyzer(self.parser)
        ]

    def extract_method_code(self, source_code: str, start_line: int, end_line: int) -> str:
        """
        Extracts the method by knowing the starting line and the ending line.
        """
        return '\n'.join(source_code.splitlines()[start_line:end_line])

    def analyze_method(self, method_code: str) -> Dict[str, List[str]]:
        """
        Analyzes a single method.
        """
        annotations = []
        statements = []

        for filter in self.filters:
            annotations.extend(filter.find_annotations(method_code))
            statements.extend(filter.find_assertions_or_statements(method_code))
        return {
            'annotations': annotations,
            'statements': statements,
        }

    def analyze_methods_diff(self, before_code: str, after_code: str) -> Dict[str, List[str]]:
        """
        Compares annotations, statements, and selectors between two versions of the method.
        """
        before_analysis = self.analyze_method(before_code)
        after_analysis = self.analyze_method(after_code)
        annotations_diff = list(difflib.unified_diff(
            before_analysis['annotations'], after_analysis['annotations']
        ))
        statements_diff = list(difflib.unified_diff(
            before_analysis['statements'], after_analysis['statements']
        ))
        return {
            'annotations_diff': self._filter_diff(annotations_diff),
            'statements_diff': self._filter_diff(statements_diff)
        }

    def analyze_methods(self, mod) -> tuple[dict[str, list[Any]], TreeSitterParser]:
        """
        Analyzes the file and determines the changes in methods.
        """
        results = {'added': [], 'deleted': [], 'modified': [], 'renamed': []}
        before_methods = {m.name: m for m in mod.methods_before}
        after_methods = {m.name: m for m in mod.methods}

        self._analyze_deleted_methods(before_methods, after_methods, mod, results)
        self._analyze_added_methods(before_methods, after_methods, mod, results)
        self._analyze_modified_methods(before_methods, after_methods, mod, results)
        self._analyze_renamed_methods(before_methods, after_methods, mod, results)

        return results,self.parser

    def _filter_diff(self, diffs: List[str]) -> List[str]:
        """
        Filters the differences to remove irrelevant information.
        """
        return [
            line for line in diffs
            if not (line.startswith('---') or line.startswith('+++') or line.startswith('@@'))
            and (line.startswith('-') or line.startswith('+'))
        ]

    def _analyze_deleted_methods(self, before_methods, after_methods, mod, results):
        for name in before_methods.keys():
            if name not in after_methods:
                code = self.extract_method_code(
                    mod.source_code_before,
                    before_methods[name].start_line - 3,
                    before_methods[name].end_line
                )
                analysis = self.analyze_method(code)
                results['deleted'].append({
                    'name': name,
                    'annotations': analysis['annotations'],
                    'statements': analysis['statements']
                })

    def _analyze_added_methods(self, before_methods, after_methods, mod, results):
        for name in after_methods.keys():
            if name not in before_methods:
                code = self.extract_method_code(
                    mod.source_code,
                    after_methods[name].start_line - 3,
                    after_methods[name].end_line
                )
                analysis = self.analyze_method(code)
                results['added'].append({
                    'name': name,
                    'annotations': analysis['annotations'],
                    'statements': analysis['statements']
                })

    def _analyze_modified_methods(self, before_methods, after_methods, mod, results):
        for name in before_methods.keys():
            if name in after_methods:
                before_code = self.extract_method_code(
                    mod.source_code_before,
                    before_methods[name].start_line - 3,
                    before_methods[name].end_line
                )
                after_code = self.extract_method_code(
                    mod.source_code,
                    after_methods[name].start_line - 3,
                    after_methods[name].end_line
                )

                if before_code != after_code:
                    diffs = self.analyze_methods_diff(before_code, after_code)
                    results['modified'].append({
                        'name': name,
                        'annotations': diffs['annotations_diff'],
                        'statements': diffs['statements_diff']
                    })

    def _analyze_renamed_methods(self, before_methods, after_methods, mod, results):
        for before_name, before_method in before_methods.items():
            for after_name, after_method in after_methods.items():
                if (before_method.start_line - 2 == after_method.start_line - 2
                        and before_method.end_line == after_method.end_line
                        and before_method.name != after_method.name):
                    diffs = self.analyze_methods_diff(
                        self.extract_method_code(
                            mod.source_code_before,
                            before_method.start_line - 3,
                            before_method.end_line
                        ),
                        self.extract_method_code(
                            mod.source_code,
                            after_method.start_line - 3,
                            after_method.end_line
                        )
                    )
                    results['renamed'].append({
                        'old_name': before_name,
                        'new_name': after_name,
                        'annotations': diffs['annotations_diff'],
                        'statements': diffs['statements_diff']
                    })