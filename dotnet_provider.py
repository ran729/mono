import glob
import os
from typing import Set, Optional, List

import bash_client
from base_provider import MonoProvider
from cache_decorator import Cacher
from tenacity import retry, wait_fixed, stop_after_attempt

from time_decorator import Timer


class DotnetProvider(MonoProvider):
    def project_is_an_app(self, project: str) -> bool:
        with open(project) as project_file:
            return '<AppName>' in project_file.read()

    # circular dependencies fix
    @Timer()
    @Cacher(on_hit_return_value=set())
    @retry(reraise=True, wait=wait_fixed(0.3), stop=stop_after_attempt(3))
    def get_dependant_projects(self, project_name: str, cache_scope: str) -> Set[str]:
        cmd = f"dotnet list {project_name} reference"
        output_lines = bash_client.execute_cmd(cmd)
        return set([os.path.basename(line.replace('\\', '/')) for line in output_lines[2:]][:1])

    def find_projects(self, prefix: str = '', recursive: Optional[bool] = False) -> List[str]:
        return glob.glob(f'{prefix}**/*.csproj', recursive=recursive)
