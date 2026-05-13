from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

import engine.models as m
import api.engine_factory as e_fac


@api_view(['GET'])
@e_fac.authorizable
def list_workouts(request, ctx):
    q = request.query_params
    role = q.get('role')
    sportsman_id = int(q.get('sportsman_id'))
    coach_id = int(q.get('coach_id'))
    batch = int(q.get('batch'))
    size = int(q.get('b_size'))

    e_wo = e_fac.get_workout_engine(ctx)
    
    wo_list = e_wo.list(role, sportsman_id, coach_id, batch,size)
    resp = [_map_wo(wo) for wo in wo_list]
    return Response(resp)


def _get_workout(request, ctx, id:int):
    q = request.query_params
    role = q.get('role')
    e_wo = e_fac.get_workout_engine(ctx)
    wo = e_wo.get_by_id(id, role)
    res = _map_wo(wo)
    return Response(res)


def _edit_workout(request, ctx, id:int):
    q = request.query_params
    role = q.get('role')
    rqst = m.UpdateWorkOutRequest(request.data)
    e_wo = e_fac.get_workout_engine(ctx)
    wo = e_wo.update(role, id, rqst)
    res = _map_wo(wo)
    return Response(res)

@api_view(['GET', 'PUT'])
@e_fac.authorizable
def get_or_edit_workout(request, ctx, id: int):
    if request.method == 'GET':
        return _get_workout(request, ctx, id)
    elif request.method == 'PUT':
        return _edit_workout(request, ctx, id)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def _map_wo(wo:m.WorkOut)->dict:
    r = {}
    r['workout'] = {k:v for k,v in wo.__dict__.items() if k != 'permission'}
    r['permissions'] = wo.permission.__dict__
    return r
