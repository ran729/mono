from abc import abstractmethod, ABC
from typing import Optional, Set, List


class MonoProvider(ABC):
    @abstractmethod
    def project_is_an_app(self, project: str) -> bool:
        pass

    @abstractmethod
    def get_dependant_projects(self, project: str, cache_scope=str) -> Set[str]:
        pass

    @abstractmethod
    def find_projects(self, prefix: str = '', recursive: Optional[bool] = False) -> List[str]:
        pass