import functools
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set, List, Optional

import git_client
from base_provider import MonoProvider
from cache_decorator import Cacher, Storage
from thread2 import ThreadWithReturnValue
from time_decorator import Timer


@dataclass
class Affected:
    changed_files: List[str]
    affected_projects: Set[str]
    affected_apps: Set[str]


class Mono:
    def __init__(self, provider: MonoProvider):
        self.provider = provider

    def get_affected_projects(self, branch: Optional[str]) -> Affected:
        csproj_to_apps = self.build_projects_to_apps_mapping()
        changed_files: List[str] = git_client.get_diff_compared_to(branch)
        changed_projects: Set[str] = self._get_changed_projects(changed_files)
        dependant_apps: Set[str] = Mono._get_dependant_apps(changed_projects, csproj_to_apps)
        return Affected(changed_files=changed_files, affected_projects=changed_projects, affected_apps=dependant_apps)

    def get_app_projects(self) -> List[str]:
        projects = self.provider.find_projects(recursive=True)
        return [os.path.basename(project) for project in projects if self.provider.project_is_an_app(project)]

    def _get_proj_deps_recursive(self, dependencies: Set[str], project_mapping: Dict[str, str], cache_scope: str) -> Set[str]:
        if len(dependencies) == 0:
            return set()

        all_deps = set()
        for index, dependency in enumerate(dependencies):
            dep_deps = self.provider.get_dependant_projects(project_mapping[dependency], cache_scope)
            all_deps = all_deps.union(dep_deps)

            recursive_deps = self._get_proj_deps_recursive(dep_deps, project_mapping, cache_scope)
            all_deps = all_deps.union(recursive_deps)

        return all_deps

    @Cacher(storage=Storage.File, key_fn=git_client.get_last_commit_hash)
    @Timer()
    def build_projects_to_apps_mapping(self) -> Dict[str, List]:
        project_paths: List[str] = self.provider.find_projects(recursive=True)
        project_mappings = self._get_project_path_mappings(project_paths)
        apps = [project for project in project_mappings.keys() if self.provider.project_is_an_app(project_mappings[project])]
        app_to_threads_map = {app: self.get_dependencies_of_app_thread(app, project_mappings) for app in apps}
        app_to_dependencies_map = {app: thread.join() for app, thread in app_to_threads_map.items()}
        return self._flip(app_to_dependencies_map)

    @staticmethod
    def _get_project_path_mappings(project_paths: List[str]) -> Dict[str, str]:
        return {os.path.basename(project_path): project_path for project_path in project_paths}

    @staticmethod
    def _flip(app_to_dependencies_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
        projects_to_apps: Dict[str, List[str]] = {}
        for app, app_dependencies in app_to_dependencies_map.items():
            for dep in app_dependencies:
                if dep not in projects_to_apps:
                    projects_to_apps[dep] = []

                projects_to_apps[dep].append(app)
        return projects_to_apps

    def get_dependencies_of_app(self, app_project: str, project_mappings: Dict[str, str]) -> Set[str]:
        start = datetime.now()
        print('start', app_project)
        first_line_deps = self.provider.get_dependant_projects(project_mappings[app_project], app_project)
        dependencies = self._get_proj_deps_recursive(first_line_deps, project_mappings, app_project).union(first_line_deps)
        dependencies.add(app_project)
        print('finish', app_project, datetime.now() - start)
        return dependencies

    def get_dependencies_of_app_thread(self, app_project: str, project_mappings: Dict[str, str]) -> ThreadWithReturnValue:
        thread = ThreadWithReturnValue(target=self.get_dependencies_of_app, args=(app_project, project_mappings))
        thread.start()
        return thread

    @Cacher()
    def _get_closest_csproj(self, path: str) -> Optional[str]:
        if not path:
            return None

        dir_path = os.path.dirname(path)
        projects = self.provider.find_projects(prefix=dir_path, recursive=True)
        return projects[0] if any(projects) else self._get_closest_csproj(dir_path)

    def _get_changed_projects(self, changed: List[str]) -> Set[str]:
        return set(map(self._get_closest_csproj, changed))

    @staticmethod
    def _get_dependant_apps(projects_changed: Set[str], projects_to_apps: Dict[str, List[str]]) -> Set[str]:
        apps_changed_map = list(map(lambda project: set(projects_to_apps[project]), projects_changed))

        if not any(apps_changed_map):
            return set()

        return functools.reduce(lambda accumulated, current: (accumulated or set()).union(current), apps_changed_map)
