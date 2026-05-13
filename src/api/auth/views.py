# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

import engine.models as m
import api.engine_factory as e_fac


@api_view(['GET'])
def health_check(request):
    return Response({"message": "Hello, world!"})


@api_view(['POST'])
def login(request):
    rqst = m.LoginRequest(request.data)
    e_auth = e_fac.get_auth_engine()
    res, token = e_auth.login(rqst)
    return Response({"auth_token": token})

@api_view(['POST'])
def register(request):
    rqst = m.RegistrationRequest(request.data)
    e_auth = e_fac.get_auth_engine()
    resp = e_auth.register_or_trigger(rqst)
    return Response(resp.__dict__)
