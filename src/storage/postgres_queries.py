from typing import LiteralString, Any
from collections.abc import Iterable

from .postgres_base_provider import BaseQuery, ArgsRangeQueryIssue
from .entities import (PersonEntity
                       , WorkOutEntity
                       , PermissionEntity)


class WorkOutByIdQuery(BaseQuery[WorkOutEntity]):
    def __init__(self, id: int) -> None:
        if id <= 0:
            issue = ArgsRangeQueryIssue('provided id value must be greater than 0')
            issue.entity = WorkOutEntity.__name__
            issue.query_args = (id,)
            raise issue
        self._id: int = id

    @property
    def sql(self) -> LiteralString:
        query = (
            "SELECT w.*, "
            "   sp.first_name as s_fname, sp.last_name as s_lname,"
            "   cp.first_name as c_fname, cp.last_name as c_lname"
            "   FROM workout w"
            "       LEFT join person sp ON w.sportsman_id = sp.id"
            "       LEFT join person cp ON w.coach_id = cp.id"
            "           WHERE w.id = %s"
        )
        return query

    @property
    def args(self) -> tuple:
        return self._id,

    def populate(self, data: list[tuple], columns: list[Any]) -> WorkOutEntity:
        if len(columns) == 0 or len(data) == 0:
            return WorkOutEntity({})
        
        row = data[0]
        return WorkOutEntity({ k:v for k, v in zip(columns, row) })


class WorkoutBatchQuery(BaseQuery[Iterable[WorkOutEntity]]):
    def __init__(self, batch: int, size: int, sportsman_id:int, coach_id:int) -> None:
        self.batch:int = batch
        self.size:int = size
        self.sportsman_id:int = sportsman_id
        self.coach_id:int = coach_id
    
    @property
    def sql(self) -> LiteralString:
        query = (
            "WITH cte AS ("
            "   SELECT p.id, p.first_name as fname, p.last_name as lname"
            "   FROM person p"
            "   WHERE p.id in (%s,%s))"

            "SELECT w.*,"
            "   sp.fname as s_fname, sp.lname as s_lname,"
            "   cp.fname as c_fname, cp.lname as c_lname"
            " FROM workout w"
            " LEFT join cte sp ON w.sportsman_id = sp.id"
            " LEFT join cte cp ON w.coach_id = cp.id"
            " WHERE w.sportsman_id = %s AND w.coach_id = %s"
            " ORDER BY id DESC LIMIT %s OFFSET %s"
        )
        return query

    @property
    def args(self) -> tuple:
        if self.sportsman_id:
            return self.sportsman_id, self.coach_id, self.sportsman_id, self.coach_id, self.size, (self.batch - 1)*self.size
        else:
            return self.size, (self.batch - 1)*self.size

    def populate(self, data: list[tuple], columns: list[Any]) -> Iterable[WorkOutEntity]:
        if len(columns) == 0 or len(data) == 0:
            return list[WorkOutEntity]()
        
        for row in data:
            yield WorkOutEntity({ k:v for k, v in zip(columns, row)})


class PersonByIdQuery(BaseQuery[PersonEntity]):
    def __init__(self, id: int, include_roles:bool, only_active:bool=True) -> None:
        if id <= 0:
            issue = ArgsRangeQueryIssue('provided id value must be greater than 0')
            issue.entity = PersonEntity.__name__
            issue.query_args = (id,)
            raise issue
        self.id:int = id
        self.include_roles:bool = include_roles
        self.only_active:bool = only_active

    @property
    def sql(self) -> LiteralString:
        if self.include_roles:
            query = (
                "SELECT p.*, STRING_AGG(pr.role, ',') as roles " 
                "FROM person p "
                "LEFT JOIN person_role pr ON p.id = pr.person_id "
                "WHERE p.id = %s "
            )
            active_predicate = "AND p.is_active = true " if self.only_active else ""
            query = query + active_predicate + "GROUP BY p.id LIMIT 1 "

            return query
        else:
            return "SELECT * FROM person WHERE id = %s LIMIT 1"

    @property
    def args(self) -> tuple:
        return self.id,

    def populate(self, data: list[tuple], columns: list[Any]) -> PersonEntity:
        if len(columns) == 0 or len(data) == 0:
            return PersonEntity({})
        
        row = data[0]
        return PersonEntity({k: (v if k!='roles' else str.split(v,',')) for k, v in zip(columns, row)})


class PersonByEmailQuery(BaseQuery[PersonEntity]):

    def __init__(self, email: str, include_roles:bool) -> None:
        if email is None or email == '':
            issue = ArgsRangeQueryIssue('provided email value must be not empty')
            issue.entity = PersonEntity.__name__
            issue.query_args = (email,)
            raise issue
        self._email:str = email
        self._include_roles:bool = include_roles

    @property
    def sql(self) -> LiteralString:
        if self._include_roles:
            sql = "SELECT  p.*, STRING_AGG(pr.role, ',') as roles FROM person p"
            sql = sql + " LEFT JOIN person_role pr ON p.id = pr.person_id WHERE email = %s GROUP BY p.id LIMIT 1"
        else:
            sql = "SELECT * FROM person WHERE email = %s LIMIT 1"

        return sql

    @property
    def args(self) -> tuple:
        return (self._email,)

    def populate(self, data: list[tuple], columns: list[Any]) -> PersonEntity:
        if len(columns) == 0 or len(data) == 0:
            return PersonEntity({})
        
        row = data[0]
        return PersonEntity({k: (v if k!='roles' else str.split(v,',')) for k, v in zip(columns, row)})
        

class PersonsBatchQuery(BaseQuery[Iterable[PersonEntity]]):
    def __init__(self, batch: int, size: int,only_active:bool=True) -> None:
        self.batch:int = batch
        self.size:int = size
        self.only_active:bool = only_active

    @property
    def sql(self) -> LiteralString:
        query = "SELECT * FROM person p "
        active_predicate = "WHERE p.is_active = true " if self.only_active else ""
        query += active_predicate + "ORDER BY id DESC LIMIT %s OFFSET %s"
        return query

    @property
    def args(self) -> tuple:
        return self.size, (self.batch - 1)*self.size

    def populate(self, data: list[tuple], columns: list[Any]) -> Iterable[PersonEntity]:
        if len(columns) == 0:
            return list[PersonEntity]()

        for row in data:
            yield PersonEntity({ k:v for k, v in zip(columns, row)})


class PersonPermissionsQuery(BaseQuery[Iterable[PermissionEntity]]):
    def __init__(self, entity: str, role: str, mode: str, person_id: int) -> None:
        self._entity: str = entity
        self._role: str = role
        self._mode: str = mode
        self._person_id: int = person_id

    @property
    def sql(self) -> LiteralString:
        sql = "SELECT * FROM permissions p WHERE p.entity = %s AND p.role = %s AND p.mode = %s AND (p.person_id IS NULL OR p.person_id = %s)"
        return sql

    @property
    def args(self) -> tuple:
        return self._entity, self._role, self._mode, self._person_id

    def populate(self, data: list[tuple], columns: list[Any]) -> Iterable[PermissionEntity]:
        if len(columns) == 0 or len(data) == 0:
            return list[PermissionEntity]()
        
        for row in data:
            yield PermissionEntity({ k:v for k, v in zip(columns, row)})


class PermissionsQuery(BaseQuery[Iterable[PermissionEntity]]):
    def __init__(self
                , id:int|None
                , entity: str|None
                , role: str|None, only_default: bool, person_id: int|None, mode: str|None
                , batch: int, b_size:int) -> None:
        super().__init__()
        self.id: int|None = id
        self.entity: str|None = entity
        self.role: str|None = role
        self.only_default: bool = only_default
        self.person_id: int|None = person_id
        self.mode: str|None = mode
        self.batch: int = batch
        self.b_size: int = b_size
        self._args: list = []

    @property
    def sql(self) -> LiteralString:
        query = "SELECT * FROM permissions p "
        
        predicates:list[LiteralString] = []
        if self.id is not None:
            predicates.append(" p.id = %s ")
            self._args.append(self.id)
        if self.entity is not None:
            predicates.append(" p.entity = %s ")
            self._args.append(self.entity)
        if self.role is not None:
            predicates.append(" p.role = %s ")
            self._args.append(self.role)
        if self.mode is not None:
            predicates.append(" p.mode = %s ")
            self._args.append(self.mode)
        
        if self.only_default:
            predicates.append(" p.person_id IS NULL ")
        elif self.person_id is not None:
            predicates.append(" ( p.person_id IS NULL OR p.person_id = %s ) ")
            self._args.append(self.person_id)

        if len(predicates) == 1:
            query += " WHERE " + predicates[0]
        elif len(predicates) > 1:
            predicate = " AND ".join(predicates)
            query += " WHERE " + predicate
        
        query += " ORDER BY entity,id LIMIT %s OFFSET %s "
        self._args.append(self.b_size)
        self._args.append((self.batch-1)*self.b_size)
        return query

    @property
    def args(self) -> tuple:
        return tuple(self._args)

    def populate(self, data: list[tuple], columns: list[Any]) -> Iterable[PermissionEntity]:
        if len(columns) == 0 or len(data) == 0:
            return list[PermissionEntity]()
        
        for row in data:
            yield PermissionEntity({ k:v for k, v in zip(columns, row)})
