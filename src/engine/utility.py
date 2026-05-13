import bcrypt
import jwt
from typing import Any

class JwtExpiredWarning(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidJwtIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def protect_with_hash(value: str, solt: str|None = None) -> str:
    password = value.encode('utf-8')
    _solt = None
    if solt is not None:
        _solt = solt.encode('utf-8')
    else:
        _solt = bcrypt.gensalt()

    hash = bcrypt.hashpw(password, _solt)
    return hash.decode('utf-8')


def verify_hash(value: str, hash: str) -> bool:
    val = value.encode('utf-8')
    return bcrypt.checkpw(val, hash.encode('utf-8')) 


def generate_jwt(secret_key: str|bytes, payload: dict):
    return jwt.encode(payload, secret_key, algorithm="HS256")

def verify_jwt(token, secret_key) -> tuple[bool, dict[str, Any]]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return True, payload
    except jwt.ExpiredSignatureError as e:
        raise JwtExpiredWarning(str(e))
    except jwt.InvalidTokenError as e:
        raise InvalidJwtIssue(str(e))