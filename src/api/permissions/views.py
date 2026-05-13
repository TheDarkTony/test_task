from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

import engine.models as m
import api.engine_factory as e_fac
from types import SimpleNamespace


@api_view(['GET'])
@e_fac.authorizable
def query_permissions(request, ctx):
    q = request.query_params
    role = q.get('role')
    entity = q.get('entity')
    batch = int(q.get('batch')) if q.get('batch') is not None else 1
    size = int(q.get('b_size')) if q.get('b_size') is not None else 1
    id = int(q.get('id')) if q.get('id') is not None else None
    person_id = int(q.get('person_id')) if q.get('person_id') is not None else None
    only_defaut = bool(q.get('only_defaut')) if q.get('only_defaut') is not None else False
    mode = q.get('mode')

    e_perm = e_fac.get_permissions_engine(ctx)
    perm_list = e_perm.query(entity, role, batch, size, id, person_id, only_defaut, mode)
    resp = [_map_perm(perm) for perm in perm_list]
    return Response(resp)

@api_view(['POST'])
@e_fac.authorizable
def create_default_permission(request, ctx):
    perm = request.data
    perm = SimpleNamespace(**perm)
    e_perm = e_fac.get_permissions_engine(ctx)
    perm_id = e_perm.create_default_permissions(perm.entity, perm.role, perm.mode)
    return Response({"permission_id": perm_id})

@api_view(['PUT'])
@e_fac.authorizable
def edit_options(request, ctx, id:int):
    rqst = m.PermissionSubjectRequest(request.data)
    e_perm = e_fac.get_permissions_engine(ctx)
    res = e_perm.edit_options(id, rqst)
    return Response({"updated": res})


@api_view(['POST'])
@e_fac.authorizable
def assign_custom_permission(request, ctx, base_perm_id:int, person_id:int):
    rqst = m.PermissionSubjectRequest(request.data)
    e_perm = e_fac.get_permissions_engine(ctx)
    res = e_perm.assign_custom_permission(base_perm_id,person_id, rqst)
    return Response({"updated": res})


def _map_perm(perm:m.EntityPermission) -> dict:
    return perm.__dict__
