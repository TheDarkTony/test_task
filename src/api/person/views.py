from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

import engine.models as m
import api.engine_factory as e_fac


@api_view(['GET'])
@e_fac.authorizable
def list_persons(request, ctx):
    q = request.query_params
    role = q.get('role')
    batch = int(q.get('batch'))
    size = int(q.get('b_size'))

    e_prsn = e_fac.get_person_engine(ctx)
    prsn_list = e_prsn.list(role, batch,size)
    resp = [_map_prsn(prsn) for prsn in prsn_list]
    return Response(resp)

def get_person(request, ctx, id:int):
    q = request.query_params
    role = q.get('role')
    
    e_prsn = e_fac.get_person_engine(ctx)
    prsn = e_prsn.get_by_id(id, role)
    res = _map_prsn(prsn)
    return Response(res)


def edit_person(request, ctx, id:int):
    q = request.query_params
    role = q.get('role')
    rqst = m.UpdatePersonRequest(request.data)
   
    e_prsn = e_fac.get_person_engine(ctx)
    prsn = e_prsn.update(role, id, rqst)
    res = _map_prsn(prsn)
    return Response(res)


@api_view(['PUT'])
@e_fac.authorizable
def person_leaving(request, ctx, id:int):
    q = request.query_params
    role = q.get('role')
   
    e_prsn = e_fac.get_person_engine(ctx)
    res = e_prsn.leave_person(role, id)
    return Response(res)


@api_view(['GET', 'PUT'])
@e_fac.authorizable
def get_or_edit_person(request, ctx, id: int):
    if request.method == 'GET':
        return get_person(request, ctx, id)
    elif request.method == 'PUT':
        return edit_person(request, ctx, id)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def _map_prsn(wo:m.Person)->dict:
    r = {}
    r['person'] = {k:v for k,v in wo.__dict__.items() if k != 'permission'}
    r['permissions'] = wo.permission.__dict__
    return r
