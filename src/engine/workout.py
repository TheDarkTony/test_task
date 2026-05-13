from collections.abc import Iterable

from .models import WorkOut, UpdateWorkOutRequest, RequestContext,PermissionSubject
from .issues import ForbiddenAccessIssue, NotFoundResourseIssue

from storage.abc_provider import IPersonProvider, IPermissionsProvider, IWorkOutProvider
from storage.entities import PermissionEntity, WorkOutEntity, PersonEntity


_ENTITY = 'workout'


class WorkOutEngine:

    def __init__(self
                 , person_provider: IPersonProvider
                 , permissions_provider: IPermissionsProvider
                 , wo_provider: IWorkOutProvider
                 , rqst_ctx: RequestContext) -> None:
        self._person_provider: IPersonProvider = person_provider
        self._permissions_provider: IPermissionsProvider = permissions_provider
        self._wo_provider: IWorkOutProvider = wo_provider
        self._ctx: RequestContext = rqst_ctx

    def get_by_id(self, id: int, role: str) -> WorkOut:
        current_prsn = self._get_current_person()
        if current_prsn.roles is None or role not in current_prsn.roles:
            raise ForbiddenAccessIssue("You have no access")

        wo = self._wo_provider.get_by_id(id)
        if wo.id == 0:
            raise NotFoundResourseIssue(f"{_ENTITY} has not been found")
        
        mode = self._mode(role, wo.sportsman_id, wo.coach_id)
        permission = self._get_permissions(role, mode, current_prsn.id)
        if not permission.allow_read:
            raise ForbiddenAccessIssue(f"You have no access to read {_ENTITY}")
        
        return self._to_workout_model(wo, permission)

    def list(self, role: str, sportsman_id: int, coach_id: int, batch: int, size: int) -> Iterable[WorkOut]:
        current_prsn = self._get_current_person()
        if current_prsn.roles is None or role not in current_prsn.roles:
            raise ForbiddenAccessIssue("You have no access to record")

        mode = self._mode(role, sportsman_id, coach_id)
        permission = self._get_permissions(role, mode, current_prsn.id)
        if not permission.allow_read:
            raise ForbiddenAccessIssue(f"You have no access to read {_ENTITY}")

        for wo in self._wo_provider.list(batch, size, sportsman_id, coach_id):
            yield self._to_workout_model(wo, permission)

    def update(self, role: str, id: int, rqst: UpdateWorkOutRequest) -> WorkOut:
        current_prsn = self._get_current_person()
        if current_prsn.roles is None or role not in current_prsn.roles:
            raise ForbiddenAccessIssue("You have no access")

        wo = self._wo_provider.get_by_id(id)
        if wo.id == 0:
            raise NotFoundResourseIssue(f"{_ENTITY} has not been found")

        mode = self._mode(role, wo.sportsman_id, wo.coach_id)
        permission = self._get_permissions(role, mode, current_prsn.id)
        if not permission.allow_edit:
            raise ForbiddenAccessIssue(f"You have no access to edit {_ENTITY}")
        
        wo.activity = rqst.activity
        wo.description = rqst.description
        wo.date = rqst.date
        wo.result = rqst.result

        wo = self._wo_provider.save(wo)
        return self._to_workout_model(wo, permission)
    
    def _mode(self, role: str, s_id:int, c_id:int) -> str:
        mode = 'other'
        if role == 'sportsman':
            mode = self._ctx.mode(s_id)
        elif role == 'coach':
            mode = self._ctx.mode(c_id)
        return mode
    
    def _get_permissions(self, role:str, mode:str, prsn_id: int):
        permission = self._permissions_provider.get_first(_ENTITY, role, mode, prsn_id)
        if permission is None:
            raise ForbiddenAccessIssue('You have no granted access')
        return permission
    
    def _get_current_person(self):
        current_prsn = self._person_provider.get_by_id(self._ctx.person_id, True)
        if current_prsn.id == 0:
            raise NotFoundResourseIssue(f"person has not been found")
        return current_prsn
    
    def _to_workout_model(self, wo, permission) -> WorkOut:
        perm = PermissionSubject()
        perm.allow_create = permission.allow_create
        perm.allow_edit = permission.allow_edit
        perm.allow_read = permission.allow_read

        model = WorkOut()
        model.id = wo.id
        model.activity = wo.activity
        model.date = wo.date
        model.result = wo.result
        model.description = wo.description
        model.coach_id = wo.coach_id
        model.sportsman_id = wo.sportsman_id
        model.coach_fname = wo.c_fname
        model.coach_lname = wo.c_lname
        model.sportsman_fname = wo.s_fname
        model.sportsman_lname = wo.s_lname
        model.permission = perm
        return model
