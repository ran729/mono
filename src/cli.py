from typing import Optional
import fire

from dotnet_provider import DotnetProvider
from mono import Mono
import logging

class MonoCli:
    def __init__(self):
        self.logger = logging.getLogger("mono")
        self.mono = Mono(DotnetProvider())

    def affected(self, branch: Optional[str] = None):
        affected = self.mono.get_affected_projects(branch)
        print(f"*************************************************")
        print(f"*************************************************")
        print(f"Files Changed: {affected.changed_files}")
        print(f"Projects affected: {affected.affected_projects}")
        print(f"******* Please build the following apps")
        return affected.affected_apps

    def build(self):
        return self.mono.build_projects_to_apps_mapping()

    def apps(self):
        return self.mono.get_app_projects()


if __name__ == '__main__':
    fire.Fire(MonoCli)
