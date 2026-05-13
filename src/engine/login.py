from datetime import datetime, timezone, timedelta

from .models import RegistrationRequest, LoginRequest
from .issues import (ValidationDataIssue
                     , NotFoundResourseIssue
                     , InvalidPasswordValidationIssue
                     , InvalidStateIssue)
from .utility import protect_with_hash, verify_hash, generate_jwt

from storage.abc_provider import IPersonProvider
from storage.entities import PersonEntity


class LoginConfig:
    def __init__(self) -> None:
        self.enabled_email_2fa: bool = False
        self.jwt_secret_key: str|bytes


class RegistrationResult:
        def __init__(self) -> None:
            self.msg: str
            self.code: int

class LoginEngine:
    def __init__(self, config: LoginConfig
                 , personProvider: IPersonProvider) -> None:
        self._cfg = config
        self._prsnProvider: IPersonProvider = personProvider

    def login(self, rqst:LoginRequest) -> tuple[bool, str]:
        rqst.validate()

        prsn = self._prsnProvider.get_by_email(rqst.email, True)
        if prsn.id <= 0:
            raise ValidationDataIssue('Provided email has not been found.')
        
        if not prsn.is_active:
            raise NotFoundResourseIssue('Person has been deleted.')
        
        roles = prsn.roles
        if roles is None or len(roles) == 0:
            issue = InvalidStateIssue("Person with undefined role")
            issue.add_note(f'email: {rqst.email}')
            raise issue
        
        if not verify_hash(rqst.pwd, prsn.password):
            raise InvalidPasswordValidationIssue("Invalid password.")
        
        claims = {
            "person_id": prsn.id,
            "roles": roles,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }

        token = generate_jwt(self._cfg.jwt_secret_key, claims)
        return True, token

    def register_or_trigger(self, rqst: RegistrationRequest) -> RegistrationResult:
        rqst.validate()

        prsn = self._prsnProvider.get_by_email(rqst.email, False)
        if prsn.id > 0:
            raise ValidationDataIssue('Provided email has already been registred.')
        
        if self._cfg.enabled_email_2fa:
            #TODO:handling email verification
            result = RegistrationResult()
            result.msg = "Please send code from email you are going to receive"
            result.code = 2
            return result

        entry = PersonEntity({})
        entry.first_name = rqst.fname
        entry.last_name = rqst.lname
        entry.email = rqst.email
        entry.email_2fa_enabled = False
        entry.email_verified = False
        entry.password = protect_with_hash(rqst.pwd)
        entry.created_at = str(datetime.now())
        
        self._prsnProvider.save(entry)

        rst = RegistrationResult()
        rst.msg = "Welcome to club"
        rst.code = 1

        return rst

