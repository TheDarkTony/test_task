from .issues import ValidationRequestIssue

class RequestContext:
    def __init__(self, claims) -> None:
        self.person_id: int
        self.roles:list[str]
        self._data = claims

    def __getattr__(self, name):
        return self._data.get(name)

    def mode(self, id:int) -> str:
        return 'self' if self.person_id == id else 'other'


class BaseRequest:

    def __init__(self, data:dict) -> None:
        self._data:dict = data

    def __getattr__(self, name):
        return self._data.get(name)

    def validate(self) -> None:
        return
    
    def _is_in_range(self, value, min:int, max:int)->bool:
        size = len(value)
        return min < size or size < max


class PermissionSubject:
    def __init__(self) -> None:
        self.allow_read: bool
        self.allow_create: bool
        self.allow_edit: bool


class EntityPermission(PermissionSubject):
    def __init__(self) -> None:
        super().__init__()
        self.id: int
        self.entity: str
        self.person_id: int|None
        self.mode:str
        self.role:str


class PermissionSubjectRequest(BaseRequest, PermissionSubject):
    def __init__(self, data: dict) -> None:
        super().__init__(data)


class LoginRequest(BaseRequest):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.pwd: str
        self.email: str
    

    def validate(self) -> None:
        if self.email is None: 
            raise ValidationRequestIssue('Email is required.')

        if not self._is_in_range(self.email, 1, 50):
            raise ValidationRequestIssue("Invalid size of email.")
        
        if '@' not in self.email:
            raise ValidationRequestIssue('Invalid value of email.')
        
        if self.pwd is None: 
            raise ValidationRequestIssue('Password is required.')


class RegistrationRequest(BaseRequest):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.fname: str
        self.lname: str
        self.email: str
        self.pwd: str
        self.pwd_confirmation: str
    

    def validate(self) -> None:
        if self.fname is None: 
            raise ValidationRequestIssue('First name is required.')

        if not self._is_in_range(self.fname, 1, 50):
            raise ValidationRequestIssue("Invalid size of first name.")

        if self.lname is None: 
            raise ValidationRequestIssue('Last name is required.')

        if not self._is_in_range(self.fname, 1, 50):
            raise ValidationRequestIssue("Invalid size of last name")
        
        if self.email is None: 
            raise ValidationRequestIssue('Email is required.')

        if not self._is_in_range(self.email, 1, 50):
            raise ValidationRequestIssue("Invalid size of email.")
        
        if '@' not in self.email:
            raise ValidationRequestIssue('Invalid value of email.')
        
        if self.pwd is None: 
            raise ValidationRequestIssue('Password is required.')

        if not self._is_in_range(self.pwd, 1, 50):
            raise ValidationRequestIssue("invalid size of password.")
        
        if self.pwd != self.pwd_confirmation:
            raise ValidationRequestIssue("Passwords do not match.")


class BaseModel:
    def __init__(self) -> None:
        self.permission: PermissionSubject


class PersonSubject:
    def __init__(self) -> None:
        self.fname: str
        self.lname: str
        self.email: str
        self.email_2fa_enabled: bool


class Person(BaseModel, PersonSubject):
    def __init__(self) -> None:
        super().__init__()
        self.id: int
        self.created_at: str
        self.email_verified: bool
        

class UpdatePersonRequest(BaseRequest, PersonSubject):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.is_active: bool

    def validate(self) -> None:
        if self.fname is None: 
            raise ValidationRequestIssue('First name is required.')

        if not self._is_in_range(self.fname, 1, 50):
            raise ValidationRequestIssue("Invalid size of first name.")

        if self.lname is None: 
            raise ValidationRequestIssue('Last name is required.')

        if not self._is_in_range(self.fname, 1, 50):
            raise ValidationRequestIssue("Invalid size of last name")
        
        if self.email is None: 
            raise ValidationRequestIssue('Email is required.')

        if not self._is_in_range(self.email, 1, 50):
            raise ValidationRequestIssue("Invalid size of email.")
        
        if '@' not in self.email:
            raise ValidationRequestIssue('Invalid value of email.')


class WorkOutSubject:
    def __init__(self) -> None:
        self.description: str
        self.activity: str
        self.result: str
        self.date: str


class WorkOut(BaseModel, WorkOutSubject):
    def __init__(self) -> None:
        super().__init__()
        self.id: int
        self.sportsman_fname: str
        self.sportsman_lname: str
        self.coach_fname: str
        self.coach_lname: str
        self.sportsman_id:int
        self.coach_id:int


class UpdateWorkOutRequest(BaseRequest, WorkOutSubject):
    def __init__(self, data: dict) -> None:
        super().__init__(data)

    def validate(self) -> None:
        if self.description is None: 
            raise ValidationRequestIssue('Description is required.')
        if self.activity is None:
            raise ValidationRequestIssue('Activity is required.')
        if self.date is None:
            raise ValidationRequestIssue('Date is required.')

        if self.result is not None and not self._is_in_range(self.result, 1, 200): 
            raise ValidationRequestIssue("Invalid size of result")
        if not self._is_in_range(self.description, 1, 100):
            raise ValidationRequestIssue("Invalid size of last name")
        if not self._is_in_range(self.activity, 1, 200):
            raise ValidationRequestIssue("Invalid size of last name")