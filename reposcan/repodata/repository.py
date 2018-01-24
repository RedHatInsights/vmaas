from cli.logger import SimpleLogger


class Repository:
    def __init__(self, repo_url):
        self.logger = SimpleLogger()
        self.repo_url = repo_url
        self.repomd = None
        self.primary = None
        self.updateinfo = None
        self.md_files = {}
        self.tmp_directory = None

    def get_package_count(self):
        if self.primary:
            return self.primary.get_package_count()
        return 0

    def get_update_count(self, update_type=None):
        return len(self.list_updates(update_type=update_type))

    def list_packages(self):
        if self.primary:
            return self.primary.list_packages()
        return []

    def list_updates(self, update_type=None):
        if self.updateinfo:
            if update_type:
                return [u for u in self.updateinfo.list_updates() if u["type"] == update_type]
            return self.updateinfo.list_updates()
        return []
