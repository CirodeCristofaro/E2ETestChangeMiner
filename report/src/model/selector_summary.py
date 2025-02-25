class SelectorSummary:
    def __init__(self, row):
        (
            self.repository_name,
            self.commit_id,
            self.delta,
            self.modified_file,
            self.type_of_change_to_the_file,
            self.type_of_change_to_the_method,
            self.method_name,
            self.statement_removed,
            self.statement_added,
            self.statement_modified,
            self.before_selector,
            self.after_selector
        ) = row
        self.changed_from_by_id = 0
        self.remained_by_id = 0
        self.changed_from_by_name = 0
        self.remained_by_name = 0
        self.changed_from_by_className = 0
        self.remained_by_className = 0
        self.changed_from_by_tagName = 0
        self.remained_by_tagName = 0
        self.changed_from_by_linkText = 0
        self.remained_by_linkText = 0
        self.changed_from_by_partialLinkText = 0
        self.remained_by_partialLinkText = 0
        self.changed_from_by_cssSelector = 0
        self.remained_by_cssSelector = 0
        self.changed_from_by_xpath = 0
        self.remained_by_xpath = 0

    def __repr__(self):
        return (f"SelectorSummary(repository_name={self.repository_name}, commit_id={self.commit_id}, "
                f"modified_file={self.modified_file}, type_of_change_to_the_file={self.type_of_change_to_the_file}, "
                f"type_of_change_to_the_method={self.type_of_change_to_the_method}, method_name={self.method_name}, "
                f"statement_removed={self.statement_removed}, statement_added={self.statement_added}, "
                f"statement_modified={self.statement_modified}, before_selector={self.before_selector}, "
                f"after_selector={self.after_selector}, changed_from_by_id={self.changed_from_by_id}, "
                f"remained_by_id={self.remained_by_id}, changed_from_by_name={self.changed_from_by_name}, "
                f"remained_by_name={self.remained_by_name}, changed_from_by_className={self.changed_from_by_className}, "
                f"remained_by_className={self.remained_by_className}, changed_from_by_tagName={self.changed_from_by_tagName}, "
                f"remained_by_tagName={self.remained_by_tagName}, changed_from_by_linkText={self.changed_from_by_linkText}, "
                f"remained_by_linkText={self.remained_by_linkText}, changed_from_by_partialLinkText={self.changed_from_by_partialLinkText}, "
                f"remained_by_partialLinkText={self.remained_by_partialLinkText}, changed_from_by_cssSelector={self.changed_from_by_cssSelector}, "
                f"remained_by_cssSelector={self.remained_by_cssSelector}, changed_from_by_xpath={self.changed_from_by_xpath}, "
                f"remained_by_xpath={self.remained_by_xpath})")