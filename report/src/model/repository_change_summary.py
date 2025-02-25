class RepositoryChangeSummary:
    def __init__(self, row):
        (
            self.repository_name,
            self.total_commit,
            self.total_commits_test,
            self.total_changes_to_files,
            self.deleted_files_count,
            self.rename_files_count,
            self.added_files_count,
            self.modified_files_count,
            self.total_selector_modify,

            self.changed_from_By_id,
            self.remained_By_id,

            self.changed_from_By_name,
            self.remained_By_name,

            self.changed_from_By_className,
            self.remained_By_className,

            self.changed_from_By_tagName,
            self.remained_By_tagName,

            self.changed_from_By_linkText,
            self.remained_By_linkText,

            self.changed_from_By_partialLinkText,
            self.remained_By_partialLinkText,

            self.changed_from_By_cssSelector,
            self.remained_By_cssSelector,

            self.changed_from_By_xpath,
            self.remained_By_xpath
        ) = row


    def percentage_commits_test(self):
        """Percentuale di commit che modificano i test"""
        return (self.total_commits_test / self.total_commit) * 100 if self.total_commit > 0 else 0

    def percentage_added(self):
        """Percentuale di file aggiunti"""
        return (self.added_files_count / self.total_commits_test) * 100 if self.total_commits_test > 0 else 0

    def percentage_modified(self):
        """Percentuale di file modificati"""
        return (self.modified_files_count / self.total_commits_test) * 100 if self.total_commits_test > 0 else 0

    def percentage_deleted(self):
        """Percentuale di file eliminati"""
        return (self.deleted_files_count / self.total_commits_test) * 100 if self.total_commits_test > 0 else 0

    def percentage_selector_modify(self):
        """Percentuale di modifiche sui selettori"""
        return (self.total_selector_modify / self.total_commits_test) * 100 if self.total_commits_test > 0 else 0

    def total_commits(self):
        return self.total_commit

    def repository_name(self):
        return self.repository_name
    def percentage_by_id_changes_selectors(self):
        return (self.changed_from_By_id / self.total_selector_modify) * 100  if self.total_selector_modify > 0 else 0

    def percentage_by_id_unchanged_selectors(self):
        return (self.remained_By_id / self.total_selector_modify) * 100  if self.total_selector_modify > 0 else 0

    def percentage_by_className_changes_selectors(self):
        return (self.changed_from_By_className / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_className_unchanged_selectors(self):
        return (self.remained_By_className / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_name_changes_selectors(self):
        return (self.changed_from_By_name / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_name_unchanged_selectors(self):
        return (self.remained_By_name / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_tagName_changes_selectors(self):
        return (self.changed_from_By_tagName / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_tagName_unchanged_selectors(self):
        return (self.remained_By_tagName / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_linkText_changes_selectors(self):
        return (self.changed_from_By_linkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_linkText_unchanged_selectors(self):
        return (self.remained_By_linkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_partialLinkText_changes_selectors(self):
        return (self.changed_from_By_partialLinkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_partialLinkText_unchanged_selectors(self):
        return (self.remained_By_partialLinkText / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_cssSelector_changes_selectors(self):
        return (self.changed_from_By_cssSelector / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_cssSelector_unchanged_selectors(self):
        return (self.remained_By_cssSelector / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_xpath_changes_selectors(self):
        return (self.changed_from_By_xpath / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0

    def percentage_by_xpath_unchanged_selectors(self):
        return (self.remained_By_xpath / self.total_selector_modify) * 100 if self.total_selector_modify > 0 else 0