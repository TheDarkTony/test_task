from collections.abc import Iterable

from storage.entities import PermissionEntity, WorkOutEntity

from .abc_provider import IPersonProvider, IWorkOutProvider, IPermissionsProvider
from .entities import PersonEntity
from .postgres_base_provider import DataProvider
from .postgres_commands import SavePermissionCommand, SavePersonCommand, SaveWorkOutCommand #,UpdatePersonCommand, CreatePersonCommand

from .postgres_queries import (PersonByIdQuery
                              , PersonByEmailQuery
                              , PersonsBatchQuery
                              , WorkOutByIdQuery
                              , WorkoutBatchQuery
                              , PersonPermissionsQuery
                              , PermissionsQuery)


class PersonProvider(IPersonProvider, DataProvider):
    def __init__(self, conn_creds: str) -> None:
        super().__init__(conn_creds)

    def get_by_id(self, id: int, include_roles: bool) -> PersonEntity:
        return self.get(PersonByIdQuery(id, include_roles))

    def get_by_email(self, email: str, include_roles: bool) -> PersonEntity:
        return self.get(PersonByEmailQuery(email, include_roles))

    def save(self, prsn: PersonEntity) -> PersonEntity:
        return self.commit_one(SavePersonCommand(prsn, "person", PersonEntity))

    def list(self, batch: int, size: int) -> Iterable[PersonEntity]:
        return self.get(PersonsBatchQuery(batch, size))
    

class WorkOutProvider(IWorkOutProvider, DataProvider):
    def __init__(self, conn_creds: str) -> None:
        super().__init__(conn_creds)

    def get_by_id(self, id: int) -> WorkOutEntity:
        return self.get(WorkOutByIdQuery(id))

    def save(self, wo: WorkOutEntity) -> WorkOutEntity:
        return self.get(SaveWorkOutCommand(wo, 'workout', WorkOutEntity))

    def list(self, batch: int, size: int, person_id:int, coach_id:int) -> Iterable[WorkOutEntity]:
        return self.get(WorkoutBatchQuery(batch, size, person_id, coach_id))


class PermissionsProvider(IPermissionsProvider, DataProvider):
    def __init__(self, conn_creds: str) -> None:
        super().__init__(conn_creds)
    
    def list(self, entity: str, role: str, mode: str, person_id: int) -> Iterable[PermissionEntity]:
        print('pppp')
        perms = self.get(PersonPermissionsQuery(entity, role, mode, person_id))
        perms = list(perms)
        custom = list([p for p in perms if p.person_id is not None])
        if len(custom) > 0:
            return custom
        return perms
    
    def get_first(self, entity: str, role: str, mode: str, person_id: int) -> PermissionEntity|None:
        permissions = list(self.list(entity, role, mode, person_id))
        if len(permissions) > 0:
            return permissions[0]        
        return None

    def query(self, batch: int, b_size:int, entity: str|None=None, role: str|None=None
             , id:int|None=None
             , person_id: int|None=None
             , only_default: bool=False, mode: str|None=None) -> Iterable[PermissionEntity]:
        return self.get(PermissionsQuery(id, entity, role, only_default, person_id, mode, batch, b_size))

    def save(self, entry: PermissionEntity) -> PermissionEntity:
        return self.commit_one(SavePermissionCommand(entry, "permissions", PermissionEntity))
