from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from .entities import PersonEntity, PermissionEntity, WorkOutEntity


class IPermissionsProvider(metaclass=ABCMeta):

    @abstractmethod
    def list(self, entity: str, role: str, mode: str, person_id: int) -> Iterable[PermissionEntity]:
        ...

    @abstractmethod
    def get_first(self, entity: str, role: str, mode: str, person_id: int) -> PermissionEntity|None:
        ...

    @abstractmethod
    def query(self, batch: int, b_size:int, entity: str|None=None, role: str|None=None
             , id:int|None=None
             , person_id: int|None=None
             , only_default: bool=False, mode: str|None=None) -> Iterable[PermissionEntity]:
        ...

    @abstractmethod
    def save(self, entry: PermissionEntity) -> PermissionEntity:
        ...


class IPersonProvider(metaclass=ABCMeta):

    @abstractmethod
    def get_by_id(self, id: int, include_roles: bool) -> PersonEntity:
        ...

    @abstractmethod
    def get_by_email(self, email: str, include_roles:bool) -> PersonEntity:
        ...

    @abstractmethod
    def save(self, prsn: PersonEntity) -> PersonEntity:
        ...

    @abstractmethod
    def list(self, batch: int, size: int) -> Iterable[PersonEntity]:
        ...


class IWorkOutProvider(metaclass=ABCMeta):

    @abstractmethod
    def get_by_id(self, id: int) -> WorkOutEntity:
        ...

    @abstractmethod
    def save(self, wo: WorkOutEntity) -> WorkOutEntity:
        ...

    @abstractmethod
    def list(self, batch: int, size: int, person_id:int, coach_id:int) -> Iterable[WorkOutEntity]:
        ...
