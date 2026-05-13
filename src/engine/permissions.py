from collections.abc import Iterable

from .issues import NotFoundResourseIssue, ForbiddenAccessIssue, ValidationDataIssue
from .models import EntityPermission, PermissionSubject, PermissionSubjectRequest, RequestContext
from storage.entities import PermissionEntity, PersonEntity
from storage.abc_provider import IPermissionsProvider, IPersonProvider

class PermissionsEngine:
    def __init__(self, ctx: RequestContext 
                 , perm_provider: IPermissionsProvider
                 , prsnProvider: IPersonProvider) -> None:
        self._ctx: RequestContext = ctx
        self._perm_provider: IPermissionsProvider = perm_provider
        self._prsn_provider: IPersonProvider = prsnProvider

    def query(self, entity: str, role: str|None, batch: int, b_size:int
             , id:int|None=None
             , person_id: int|None=None
             , only_defaut: bool=False, mode: str|None=None) -> Iterable[EntityPermission]:
        
        self._chk_access_to_admin()

        for item in self._perm_provider.query(batch, b_size, entity, role, id, person_id, only_defaut, mode):
            yield self._to_perm_model(item)


    def create_default_permissions(self, entity: str, role: str, mode: str) -> int:
        self._chk_access_to_admin()

        perm = self._perm_provider.query(1, 2, entity, role, only_default=True, mode=mode)
        if len(list(perm)) > 0:
            raise ValidationDataIssue("change will bring to invalid state of db")
        
        perm = PermissionEntity({})
        perm.allow_create = False
        perm.allow_edit = False
        perm.allow_read = False
        perm.role = role
        perm.mode = mode
        perm.entity = entity

        perm = self._perm_provider.save(perm)
        return perm.id

    def edit_options(self, id: int, m: PermissionSubjectRequest) -> bool:
        self._chk_access_to_admin()

        entries = self._perm_provider.query(1, 2, id=id)
        entries = list(entries)
        if len(entries) == 0:
            raise NotFoundResourseIssue("permission is not found")
        
        perm = entries[0]

        perm.allow_create = m.allow_create
        perm.allow_edit = m.allow_edit
        perm.allow_read = m.allow_read

        perm = self._perm_provider.save(perm)
        return True


    def assign_custom_permission(self, base_perm_id: int, person_id:int, options: PermissionSubject) -> bool:
        self._chk_access_to_admin()
        
        prsn = self._prsn_provider.get_by_id(person_id, True)
        if prsn.id == 0:
            raise NotFoundResourseIssue('person is not found')

        perms = self._perm_provider.query(1, 1, id=base_perm_id)
        perms = list(perms)
        if len(perms) == 0:
            raise NotFoundResourseIssue("permission is not found")
        
        perm = perms[0]
        if prsn.roles is None or perm.role not in prsn.roles:
            raise ValidationDataIssue('person is not in role of permission')
        
        available = self._perm_provider.query(1,3, person_id=person_id, role=perm.role, mode=perm.mode, entity=perm.entity)
        available = list(available)
        if len(available) >= 2:
            raise ValidationDataIssue(f'person has already had custom permission to {perm.entity}')

        custom = PermissionEntity({})
        custom.person_id = person_id
        custom.allow_create = options.allow_create
        custom.allow_edit = options.allow_edit
        custom.allow_read = options.allow_read
        custom.role = perm.role
        custom.mode = perm.mode
        custom.entity = perm.entity

        perm = self._perm_provider.save(custom)
        return True

    def _chk_access_to_admin(self) -> PersonEntity:
        prsn = self._prsn_provider.get_by_id(self._ctx.person_id, True)
        if prsn.id == 0:
            raise NotFoundResourseIssue("person is not found")
        if prsn.roles is None or 'admin' not in prsn.roles:
            raise ForbiddenAccessIssue("you have no access to administration")
        
        return prsn
    
    def _to_perm_model(self, perm: PermissionEntity) -> EntityPermission:
        m = EntityPermission()
        m.id = perm.id
        m.entity = perm.entity
        m.person_id = perm.person_id
        m.allow_read = perm.allow_read
        m.allow_create = perm.allow_create
        m.allow_edit = perm.allow_edit
        m.mode = perm.mode
        m.role = perm.role
        return m
