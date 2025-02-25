class TotalSummary:
    def __init__(self, row):
        (
            self.total_repository,
            self.total_commit,
            self.total_commits_test,
            self.total_changes_to_files,
            self.total_selector_modify,
            self.total_modified_files,
            self.total_changed_from_By_id,
            self.total_remained_By_id,

            self.total_changed_from_By_name,
            self.total_remained_By_name,

            self.total_changed_from_By_className,
            self.total_remained_By_className,

            self.total_changed_from_By_tagName,
            self.total_remained_By_tagName,

            self.total_changed_from_By_linkText,
            self.total_remained_By_linkText,

            self.total_changed_from_By_partialLinkText,
            self.total_remained_By_partialLinkText,

            self.total_changed_from_By_cssSelector,
            self.total_remained_By_cssSelector,

            self.total_changed_from_By_xpath,
            self.total_remained_By_xpath
        ) = row

    def __repr__(self):
        return (
            f"TotalSummary(total_repository={self.total_repository}, total_commit={self.total_commit}, total_commits_test={self.total_commits_test}, "
            f"total_changes_to_files={self.total_changes_to_files},total_selector_modify={self.total_selector_modify},"
            f" total_modified_files={self.total_modified_files}, "
            f"total_changed_from_By_id={self.total_changed_from_By_id}, total_remained_By_id={self.total_remained_By_id}, "
            f"total_changed_from_By_name={self.total_changed_from_By_name}, total_remained_By_name={self.total_remained_By_name}, "
            f"total_changed_from_By_className={self.total_changed_from_By_className}, total_remained_By_className={self.total_remained_By_className}, "
            f"total_changed_from_By_tagName={self.total_changed_from_By_tagName}, total_remained_By_tagName={self.total_remained_By_tagName}, "
            f"total_changed_from_By_linkText={self.total_changed_from_By_linkText}, total_remained_By_linkText={self.total_remained_By_linkText}, "
            f"total_changed_from_By_partialLinkText={self.total_changed_from_By_partialLinkText}, total_remained_By_partialLinkText={self.total_remained_By_partialLinkText}, "
            f"total_changed_from_By_cssSelector={self.total_changed_from_By_cssSelector}, total_remained_By_cssSelector={self.total_remained_By_cssSelector}, "
            f"total_changed_from_By_xpath={self.total_changed_from_By_xpath}, total_remained_By_xpath={self.total_remained_By_xpath})"
        )


    def percentage_commits_test(self):
        """Percentuale di commit che modificano i test"""
        return (self.total_commits_test / self.total_commit) * 100 if self.total_commit > 0 else 0

    def total_commits(self):
        return self.total_commit
    def percentage_by_id_changes_selectors(self):
        return (self.total_changed_from_By_id / self.total_selector_modify) * 100  if self.total_selector_modify > 0 else 0

    def percentage_by_id_unchanged_selectors(self):
        return (self.total_remained_By_id / self.total_selector_modify) * 100  if self.total_selector_modify > 0 else 0

    def percentage_by_className_changes_selectors(self):
        return (self.total_changed_from_By_className / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_className_unchanged_selectors(self):
        return (self.total_remained_By_className / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_name_changes_selectors(self):
        return (self.total_changed_from_By_name / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_name_unchanged_selectors(self):
        return (self.total_remained_By_name / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_tagName_changes_selectors(self):
        return (self.total_changed_from_By_tagName / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_tagName_unchanged_selectors(self):
        return (self.total_remained_By_tagName / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_linkText_changes_selectors(self):
        return (self.total_changed_from_By_linkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_linkText_unchanged_selectors(self):
        return (self.total_remained_By_linkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_partialLinkText_changes_selectors(self):
        return (self.total_changed_from_By_partialLinkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_partialLinkText_unchanged_selectors(self):
        return (self.total_remained_By_partialLinkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_cssSelector_changes_selectors(self):
        return (self.total_changed_from_By_cssSelector / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_cssSelector_unchanged_selectors(self):
        return (self.total_remained_By_cssSelector / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_xpath_changes_selectors(self):
        return (self.total_changed_from_By_xpath / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_xpath_unchanged_selectors(self):
        return (self.total_remained_By_xpath / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

