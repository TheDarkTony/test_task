import engine.login as e_auth
import engine.workout as e_wo
import engine.person as e_prsn
import engine.permissions as e_perm
import storage.postgres_provider as s_provider
import engine.utility as util
from engine.models import RequestContext
import engine.issues as err

from functools import wraps
from rest_framework.response import Response


from django.conf import settings
value = getattr(settings, 'MY_APP_CUSTOM_SETTING', 'default_value')

connection_creds:str = getattr(settings, "FITNESS_DB_CONNECTION_CREDS")
jwt_secret_key:str = getattr(settings, "FITNESS_JWT_SECRET_KEY")

if connection_creds is None or jwt_secret_key is None:
    raise Exception("Configuration issue")

def authorizable(func):
    #TODO: add logger
    @wraps(func)
    def wrapper(request, *args, **kwargs):        
        token:str|None = request.headers.get('Authorization')
        if token is None or not token.startswith('Bearer '):
            return Response({"error": "Please login to get access"},status=401)
        
        token = token.replace('Bearer ', '').strip()
        try:
            _, ctx = util.verify_jwt(token, jwt_secret_key)
            auth_ctx = RequestContext(ctx)            
            response = func(request, auth_ctx, *args, **kwargs)
            return response
        except (util.InvalidJwtIssue, util.JwtExpiredWarning) as issue:
            return Response({"error": str(issue)},status=401)
        except err.ForbiddenAccessIssue as ex:
            return Response({"error": str(ex)},status=403)
        except err.NotFoundResourseIssue as ex:
            return Response({"msg": str(ex)},status=404)
        except (err.InvalidPasswordValidationIssue
                , err.ValidationDataIssue, err.ValidationRequestIssue
        ) as ex:
            return Response({"msg": str(ex)},status=400)
        except Exception as e:
            return Response({"error": str(e)},status=400)

    return wrapper


def get_auth_engine():
    cfg = e_auth.LoginConfig()
    cfg.enabled_email_2fa = False
    cfg.jwt_secret_key = jwt_secret_key
    p = s_provider.PersonProvider(connection_creds)
    return e_auth.LoginEngine(cfg, p)


def get_workout_engine(ctx:RequestContext):
    wp = s_provider.WorkOutProvider(connection_creds)
    p_prov = s_provider.PersonProvider(connection_creds)
    perm_provider = s_provider.PermissionsProvider(connection_creds)
    return e_wo.WorkOutEngine(p_prov, perm_provider, wp, ctx)
    

def get_person_engine(ctx:RequestContext):
    p_prov = s_provider.PersonProvider(connection_creds)
    perm_provider = s_provider.PermissionsProvider(connection_creds)
    return e_prsn.PersonEngine(p_prov, perm_provider, ctx)

def get_permissions_engine(ctx:RequestContext):
    perm_provider = s_provider.PermissionsProvider(connection_creds)
    p_prov = s_provider.PersonProvider(connection_creds)
    return e_perm.PermissionsEngine(ctx, perm_provider, p_prov)

    
    
