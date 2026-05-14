from collections.abc import Iterable

from .models import Person, UpdatePersonRequest, RequestContext,PermissionSubject
from .issues import ValidationDataIssue, ForbiddenAccessIssue, NotFoundResourseIssue

from storage.abc_provider import IPersonProvider, IPermissionsProvider

_ENTITY = 'person'


class PersonEngine:
    def __init__(self
                 , person_provider: IPersonProvider
                 , permissions_provider: IPermissionsProvider
                 , ctx: RequestContext) -> None:
        self._person_provider: IPersonProvider = person_provider
        self._permissions_provider: IPermissionsProvider = permissions_provider
        self._ctx: RequestContext = ctx


    def get_by_id(self, id: int, role: str) -> Person:
        current_prsn = self._get_current_person()
        if not current_prsn.roles or role not in current_prsn.roles:
            raise ForbiddenAccessIssue("You have no access")

        permission = self._get_permissions(role, self._ctx.mode(id), current_prsn.id)
        if not permission.allow_read:
            raise ForbiddenAccessIssue("You have no access to read person info")

        prsn = current_prsn
        if current_prsn.id != id:
            prsn = self._person_provider.get_by_id(id, False)
            if not prsn.id:
                raise NotFoundResourseIssue("Person has not been found")
            
        return self._to_person_model(prsn, permission)

    def list(self, role: str, batch: int, size: int) -> Iterable[Person]:
        current_prsn = self._get_current_person()
        if not current_prsn.roles or role not in current_prsn.roles:
            raise ForbiddenAccessIssue("You have no access")

        permission = self._get_permissions(role, 'other', current_prsn.id)
        if not permission.allow_read:
            raise ForbiddenAccessIssue("You have no access to list people")

        for prsn in self._person_provider.list(batch, size):
            yield self._to_person_model(prsn, permission)

    def update(self, role: str, id: int, rqst: UpdatePersonRequest) -> Person:
        current_prsn = self._get_current_person()
        if not current_prsn.roles or role not in current_prsn.roles:
            raise ForbiddenAccessIssue("You are not in role")

        mode = self._ctx.mode(id)
        permission = self._get_permissions(role, mode, current_prsn.id)
        if not permission.allow_edit:
            raise ForbiddenAccessIssue("You have no access to edit person info")
        
        prsn = current_prsn
        if current_prsn.id != id:
            prsn = self._person_provider.get_by_id(id, False)
            if prsn.id == 0:
                raise NotFoundResourseIssue("Person has not been found")
        
        prsn.email = rqst.email
        prsn.email_2fa_enabled = rqst.email_2fa_enabled
        prsn.first_name = rqst.fname
        prsn.last_name = rqst.lname
        if rqst.is_active is not None:
            prsn.is_active = rqst.is_active

        prsn = self._person_provider.save(prsn)
        return self._to_person_model(prsn, permission)
    
    def leave_person(self, role: str, id: int):
        current_prsn = self._get_current_person()
        if not current_prsn.roles or role not in current_prsn.roles:
            raise ForbiddenAccessIssue("You are not in role")

        mode = self._ctx.mode(id)
        if mode != 'self':
            raise ForbiddenAccessIssue("You have no access to leave other person")

        permission = self._get_permissions(role, mode, current_prsn.id)
        if not permission.allow_edit:
            raise ForbiddenAccessIssue("You have no access to edit person info")
        
        current_prsn.is_active = False
        self._person_provider.save(current_prsn)
        return True
    
    def _get_permissions(self, role:str, mode:str, prsn_id: int):
        permission = self._permissions_provider.get_first(_ENTITY, role, mode, prsn_id)
        if permission is None:
            raise ForbiddenAccessIssue('You have no granted access')
        return permission
    
    def _get_current_person(self):
        current_prsn = self._person_provider.get_by_id(self._ctx.person_id, True)
        if current_prsn.id == 0 or not current_prsn.is_active:
            raise NotFoundResourseIssue(f"person has not been found")
        return current_prsn

    def _to_person_model(self, prsn, permission) -> Person:
        perm = PermissionSubject()
        perm.allow_create = permission.allow_create
        perm.allow_edit = permission.allow_edit
        perm.allow_read = permission.allow_read

        model = Person()
        model.id = prsn.id
        model.email = prsn.email
        model.fname = prsn.first_name
        model.lname = prsn.last_name
        model.email_verified = prsn.email_verified
        model.created_at = prsn.created_at
        model.email_2fa_enabled = prsn.email_2fa_enabled
        model.permission = perm
        return model