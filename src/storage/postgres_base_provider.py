from abc import abstractmethod, ABCMeta
from typing import LiteralString, Any
import psycopg
from .entities import BaseEntity

class NotFoundQueryIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.entity: str
        self.id:str
        self.code:int
        self.log_msg:str


class ArgsRangeQueryIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.entity: str
        self.code:int
        self.query_args:tuple
        self.log_msg:str


class InvalidOperationIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CommitFailedIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CommandValidationIssue(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class BaseQuery[TEntity](metaclass=ABCMeta):

    @property
    @abstractmethod
    def sql(self) -> LiteralString:
        ...

    @property
    @abstractmethod
    def args(self) -> tuple:
        ...

    @abstractmethod
    def populate(self, data: list[tuple], columns: list[Any]) -> TEntity:
        ...


class BaseCommand[TEntity](BaseQuery[TEntity]):

    def __init__(self, entry: TEntity) -> None:
        if isinstance(entry, BaseEntity):
            pk, val = entry.primary_key()
            if val > 0 and not entry.is_changed():
                raise CommandValidationIssue("entry is alredy in target state")
        else:
            raise Exception("record of inappropriate type provided")
        
        self._entry: BaseEntity = entry
    
    def get_data(self) -> dict[str, Any]:
        if not isinstance(self._entry, BaseEntity):
            raise InvalidOperationIssue('Provided object is not entity')
        return self._entry._data
    
    def _get_changed_props(self) -> tuple[str, ...]:
        return tuple(p for p in self._get_changed_data().keys())
    
    def _get_changed_values(self) -> tuple[Any, ...]:
        return tuple(p for p in self._get_changed_data().values())
    
    def _get_changed_data(self) -> dict[str, Any]:
        if not isinstance(self._entry, BaseEntity):
            raise InvalidOperationIssue('Provided object is not entity')
        
        if not self._entry.is_changed():
            raise InvalidOperationIssue("Entity is not changed")
        
        return self._entry._changed_data
        

class DataProvider:

    def __init__(self, conn_creds: str) -> None:
        self._connection_creds: str = conn_creds
    
    def get[TEntity](self, query: BaseQuery[TEntity]) -> TEntity:
        rows:list[tuple]
        columns:list[Any]|None = None
        sql = query.sql
        sql_args = query.args
        with psycopg.connect(self._connection_creds) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, sql_args)
                rows = cursor.fetchall()

                if cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]

        if columns is None:
            columns = list()

        return query.populate(rows, columns)

    def commit_one[TEntity](self, cmd: BaseCommand[TEntity]) -> TEntity:
        rows:list[tuple]
        columns:list[Any]|None = None
        sql = cmd.sql
        sql_args = cmd.args
        affected_rows = 0

        with psycopg.connect(self._connection_creds) as conn:
            with conn.cursor() as cursor:
                rows = cursor.execute(sql, sql_args).fetchall()
                conn.commit()

                affected_rows = cursor.rowcount
                if cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]

        if affected_rows <= 0 or columns is None:
            raise CommitFailedIssue('No records are affected')
        
        return cmd.populate(rows, columns)
