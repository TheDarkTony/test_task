from typing import Any
from functools import wraps
from abc import abstractmethod, ABCMeta


class BaseEntity(metaclass=ABCMeta):
    
    def __init__(self, data: dict[str,Any]) -> None:
        self._data: dict[str, Any] = data
        self._changed_data: dict[str, Any] = dict()
        
    def is_changed(self) -> bool:
        return len(self._changed_data) > 0
    
    @abstractmethod
    def primary_key(self) -> tuple[str, Any]:
        ...


def saveable(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        prop_name = func.__name__
        value = getattr(self, prop_name)
        new_value, = args
        if value != new_value and isinstance(self, BaseEntity):
            self._changed_data[prop_name] = new_value
        func(self, *args, ** kwargs)
    return wrapper


class PersonEntity(BaseEntity):
    def __init__(self, data: dict[str,Any]) -> None:
        super().__init__(data)

    def primary_key(self) -> tuple[str, Any]:
        return 'id', self.id

    @property
    def id(self) -> int:
        return int(self._data.get('id', 0))

    @property
    def first_name(self) -> str:
        return self._data.get('first_name', '')
    
    @first_name.setter
    @saveable
    def first_name(self, value: str) -> None:
        self._data['first_name'] = value

    @property
    def last_name(self) -> str:
        return self._data.get('last_name', '')
    
    @last_name.setter
    @saveable
    def last_name(self, value: str) -> None:
        self._data['last_name'] = value

    @property
    def email(self) -> str:
        return self._data.get('email', '')
    
    @email.setter
    @saveable
    def email(self, value: str) -> None:
        self._data['email'] = value

    @property
    def email_verified(self) -> bool:
        return bool(self._data.get('email_verified'))

    @email_verified.setter
    @saveable
    def email_verified(self, value:bool) -> None:
        self._data['email_verified'] = value

    @property
    def email_2fa_enabled(self) -> bool:
        return bool(self._data.get('email_2fa_enabled'))

    @email_2fa_enabled.setter
    @saveable
    def email_2fa_enabled(self, value: bool) -> None:
        self._data['email_2fa_enabled'] = value

    @property
    def password(self) -> str:
        return self._data.get('password') or ''

    @password.setter
    @saveable
    def password(self, value: str) -> None:
        self._data['password'] = value

    @property
    def is_active(self) -> bool:
        return bool(self._data.get('is_active'))
    
    @is_active.setter
    @saveable
    def is_active(self, value:bool) -> None:
        self._data['is_active'] = value

    @property
    def created_at(self) -> str:
        return self._data.get('created_at') or ''
    
    @created_at.setter
    @saveable
    def created_at(self, value: str) -> None:
        self._data['created_at'] = value
    
    @property
    def roles(self) -> list[str] | None:
        return self._data.get('roles')


class WorkOutEntity(BaseEntity):
    def __init__(self, data: dict[str,Any]) -> None:
        super().__init__(data)

    def primary_key(self) -> tuple[str, Any]:
        return 'id', self.id

    @property
    def id(self) -> int:
        return int(self._data.get('id', 0))

    @property
    def description(self) -> str:
        return self._data.get('description', '')
    
    @description.setter
    @saveable
    def description(self, value: str) -> None:
        self._data['description'] = value

    @property
    def date(self) -> str:
        return self._data.get('date', '')
    
    @date.setter
    @saveable
    def date(self, value: str) -> None:
        self._data['date'] = value
    
    @property
    def activity(self) -> str:
        return self._data.get('activity', '')
    
    @activity.setter
    @saveable
    def activity(self, value: str) -> None:
        self._data['activity'] = value
    
    @property
    def result(self) -> str:
        return self._data.get('result', '')
    
    @result.setter
    @saveable
    def result(self, value: str) -> None:
        self._data['result'] = value
    
    @property
    def sportsman_id(self) -> int:
        return self._data.get('sportsman_id', '')
    
    @sportsman_id.setter
    @saveable
    def sportsman_id(self, value: int) -> None:
        self._data['sportsman_id'] = value

    @property
    def coach_id(self) -> int:
        return self._data.get('coach_id', '')
    
    @coach_id.setter
    @saveable
    def coach_id(self, value: int) -> None:
        self._data['coach_id'] = value

    @property
    def c_fname(self) -> str:
        return self._data.get('c_fname', '')
    
    @property
    def c_lname(self) -> str:
        return self._data.get('c_lname', '')
    
    @property
    def s_fname(self) -> str:
        return self._data.get('s_fname', '')
    
    @property
    def s_lname(self) -> str:
        return self._data.get('s_lname', '')


class PermissionEntity(BaseEntity):
    def __init__(self, data: dict[str,Any]) -> None:
        super().__init__(data)

    def primary_key(self) -> tuple[str, Any]:
        return 'id', self.id

    @property
    def id(self) -> int:
        return int(self._data.get('id', 0))


    @property
    def entity(self) -> str:
        return self._data.get('entity', '')
    
    @entity.setter
    @saveable
    def entity(self, value: str) -> None:
        self._data['entity'] = value

    @property
    def role(self) -> str:
        return self._data.get('role', '')
    
    @role.setter
    @saveable
    def role(self, value: str) -> None:
        self._data['role'] = value
    
    @property
    def allow_create(self) -> bool:
        return bool(self._data.get('allow_create'))
    
    @allow_create.setter
    @saveable
    def allow_create(self, value: bool) -> None:
        self._data['allow_create'] = value

    
    @property
    def allow_edit(self) -> bool:
        return bool(self._data.get('allow_edit'))
    
    @allow_edit.setter
    @saveable
    def allow_edit(self, value: bool) -> None:
        self._data['allow_edit'] = value

    
    @property
    def allow_read(self) -> bool:
        return bool(self._data.get('allow_read'))
    
    @allow_read.setter
    @saveable
    def allow_read(self, value: bool) -> None:
        self._data['allow_read'] = value

    @property
    def mode(self) -> str:
        return self._data.get('mode') or ''
    
    @mode.setter
    @saveable
    def mode(self, value: str) -> None:
        self._data['mode'] = value

    
    @property
    def person_id(self) -> int|None:
        return self._data.get('person_id')
    
    @person_id.setter
    @saveable
    def person_id(self, value: int|None) -> None:
        self._data['person_id'] = value

