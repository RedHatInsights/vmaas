from cli.logger import SimpleLogger


class Repository:
    def __init__(self, repo_url, repomd, primary, updateinfo):
        self.logger = SimpleLogger()
        self.repo_url = repo_url
        self.repomd = repomd
        self.primary = primary
        self.updateinfo = updateinfo

    def get_package_count(self):
        return self.primary.get_package_count()

    def get_update_count(self, update_type=None):
        return len(self.list_updates(update_type=update_type))

    def list_packages(self):
        return self.primary.list_packages()

    def list_updates(self, update_type=None):
        if self.updateinfo:
            if update_type:
                return [u for u in self.updateinfo.list_updates() if u["type"] == update_type]
            return self.updateinfo.list_updates()
        return []
