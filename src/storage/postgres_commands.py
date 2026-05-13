from typing import LiteralString, Any, cast
from .postgres_base_provider import BaseCommand
from .entities import PersonEntity, WorkOutEntity, PermissionEntity


class SaveEntityCommand[TEntity](BaseCommand[TEntity]):
    def __init__(self, entry: TEntity, table: str, entity) -> None:
        super().__init__(entry)
        self.table: str = table
        self.__entity = entity

    @property
    def sql(self) -> LiteralString:
        pk, id = self._entry.primary_key()
        if id > 0:
            #edit
            columns = self._get_changed_props()
            kv_pairs = ",".join([f" {col} = %s " for col in columns])
            query = f"UPDATE {self.table} SET "
            query += kv_pairs
            query += f" WHERE {pk} = " + " %s" + " RETURNING *"
            return cast(LiteralString, query)
        else:
            #create
            columns = [c for c in self.get_data().keys() if c != pk]
            sql = f"INSERT INTO {self.table} ( "
            sql = sql + ",".join(columns) +" ) "
            sql = sql + " VALUES ( " + ",".join(['%s']*len(columns)) + " ) RETURNING *"
            return cast(LiteralString, sql)

    @property
    def args(self) -> tuple:
        pk, id_value = self._entry.primary_key()
        if id_value > 0:
            data = self._get_changed_data()
            values = [v for v in data.values()]
            values.append(id_value)
            return tuple(values)
        else:
            t = [v for k, v in self._entry._data.items() if k != pk]
            return tuple(t)

    def populate(self, data: list[tuple], columns: list[Any]) -> TEntity:
        if len(columns) == 0 or len(data) == 0:
            return self.__entity({})
        
        row = data[0]
        return self.__entity({ k:v for k, v in zip(columns, row)})
    

class SavePermissionCommand(SaveEntityCommand[PermissionEntity]):
    def __init__(self, entry: PermissionEntity, table: str, entity) -> None:
        super().__init__(entry, table, entity)


class SavePersonCommand(SaveEntityCommand[PersonEntity]):
    def __init__(self, entry: PersonEntity, table: str, entity) -> None:
        super().__init__(entry, table, entity)


class SaveWorkOutCommand(SaveEntityCommand[WorkOutEntity]):
    def __init__(self, entry: WorkOutEntity, table: str, entity) -> None:
        super().__init__(entry, table, entity)
