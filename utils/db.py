from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import (
    Iterable,
    Optional,
    List,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
    TYPE_CHECKING,
)
from types import TracebackType
import math
import numpy as np
import pandas as pd

import logging
import psycopg2

from .typing import AnyTuple, AnyDict
from settings import settings


if TYPE_CHECKING:
    from psycopg2 import connection as pg_connection


PROTECTED_DB = [""]
PROTECTED_TABLES = ["appsflyer", "adjust_data", "tmp_trends", "fb_burn", "taxes"]

DBResponse = List[AnyTuple]
DBQueryParams = Union[AnyTuple, AnyDict, Iterable[AnyTuple], Iterable[AnyDict]]

SLEEP_MINUTES = 5

OPTIMIZE_QUERY = """
        select concat('optimize table ',
                      database, '.',
                      table, ' partition ',
                      if(not match(partition, '.*,.*|[0-9]+'),
                      concat('\\'', partition, '\\''), partition),
                      ' final settings optimize_throw_if_noop=1, optimize_skip_merged_partitions=0;')
        from system.parts
        where table = '{target_table}'
        and database = '{target_database}'
        and active
        group by database, table, partition
        having   count()>1
        order by partition;
        """


class BaseDBHandler(metaclass=ABCMeta):
    _Self = TypeVar("_Self", bound="BaseDBHandler")

    @abstractmethod
    def __enter__(self) -> _Self:
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        ...

    @overload
    def query(self, query: str) -> DBResponse:
        ...

    @overload
    def query(self, query: str, params: AnyTuple) -> DBResponse:
        ...

    @overload
    def query(self, query: str, params: AnyDict) -> DBResponse:
        ...

    @overload
    def query(self, query: str, params: Iterable[AnyTuple]) -> DBResponse:
        ...

    @overload
    def query(self, query: str, params: Iterable[AnyDict]) -> DBResponse:
        ...

    @abstractmethod
    def query(self, query: str, params: Optional[DBQueryParams] = None) -> DBResponse:
        ...


class PostgresHandler(BaseDBHandler):
    _client: Optional["pg_connection"]

    def __init__(self) -> None:
        self._connection_url = settings.POSTGRES_URI
        self._client = None
        logging.info("Init postgres client")

    def __enter__(self) -> "pg_connection":
        self._client = psycopg2.connect(self._connection_url)
        self._client.__enter__()

        return self._client

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        assert self._client is not None

        self._client.__exit__(exc_type, exc_val, exc_tb)
        self._client.close()

        self._client = None

    def query(self, query: str, params: Optional[DBQueryParams] = None) -> DBResponse:
        with self as client:
            with client.cursor() as cursor:
                cursor.execute(query, params)
                return cast(DBResponse, cursor.fetchall())

    def query_with_columns(self, query: str, params: Optional[DBQueryParams] = None):
        with self as client:
            with client.cursor() as cursor:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                return cursor.fetchall(), columns

    def execute(self, query: str, params: Optional[DBQueryParams] = None) -> None:
        with self as client:
            with client.cursor() as cursor:
                cursor.execute(query, params)

    # function for inserting chunk to postgres database
    def insert_chunk(self, chunk, schema, table, cols):
        def addapt_numpy_float64(numpy_float64):
            return psycopg2.extensions.AsIs(numpy_float64)

        def addapt_numpy_int64(numpy_int64):
            return psycopg2.extensions.AsIs(numpy_int64)

        psycopg2.extensions.register_adapter(np.float64, addapt_numpy_float64)
        psycopg2.extensions.register_adapter(np.int64, addapt_numpy_int64)
        query = f"insert into {schema}.{table} values "
        n_columns = len(cols)
        places = ",".join(["%s"] * n_columns)
        with self as client:
            with client.cursor() as cursor:
                rows = ",".join(
                    cursor.mogrify(f"({places})", row).decode("utf-8")
                    for row in chunk.values
                )
                cursor.execute(query + rows)

    # function for upserting chunk to postgres database
    def upsert_chunk(self, query, chunk, cols):
        n_columns = len(cols)
        places = ",".join(["%s"] * n_columns)
        with self as client:
            with client.cursor() as cursor:
                rows = ",".join(
                    cursor.mogrify(f"({places})", row).decode("utf-8")
                    for row in chunk.values
                )
                cursor.execute(query % rows)


class PandasHandler:
    def __init__(self, client: Union[PostgresHandler]):
        self._client = client

    def query_dataframe(self, query, **kwargs):
        data, columns = self._client.query_with_columns(query, kwargs)
        df = pd.DataFrame(data, columns=columns)
        return df

    def insert_dataframe(
        self, data, schema, table, chunk_size=200000
    ) -> None:  # db for clickhouse is the same as schema for postgresql
        if len(data.columns) == 0:
            logging.info("Can't insert empty dataframe")
            return
        n_rows = data.shape[0]
        n_chunks = math.ceil(n_rows / chunk_size)
        chunks = np.array_split(data, n_chunks, axis=0)
        cols = data.columns

        n = 0
        for chunk in chunks:
            num_rows = len(chunk)
            n += num_rows
            logging.info(f"{n}:{n_rows}")
            self._client.insert_chunk(chunk, schema, table, cols)

        logging.info("Finished inserting")

    def upsert_dataframe(
        self, query, data, chunk_size=200000
    ) -> None:  # db for clickhouse is the same as schema for postgresql
        if len(data.columns) == 0:
            logging.info("Can't insert empty dataframe")
            return
        n_rows = data.shape[0]
        n_chunks = math.ceil(n_rows / chunk_size)
        chunks = np.array_split(data, n_chunks, axis=0)
        cols = data.columns

        n = 0
        for chunk in chunks:
            num_rows = len(chunk)
            n += num_rows
            logging.info(f"{n}:{n_rows}")
            self._client.upsert_chunk(query, chunk, cols)

        logging.info("Finished inserting")
