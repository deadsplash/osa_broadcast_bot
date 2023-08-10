from typing import List

from utils.db import PostgresHandler
from utils.logs import configure_logger

logger = configure_logger()
PG = PostgresHandler()
SCHEMA = "public"
TABLE = "users"
ADMIN_TABLE = "admin"
ALLOWED_USER_TYPES = ["new", "involved", "all"]


class UsersProcess:
    def __init__(self):
        self._pg: PostgresHandler = PostgresHandler()

    def add_user(self, chat_id: str, user_type: str = "new"):

        self._execute(
            f"INSERT INTO {SCHEMA}.{TABLE} values "
            f"('{chat_id}', '{user_type}', now())"
            f"ON CONFLICT (chat_id) DO UPDATE "
            f"SET user_type = EXCLUDED.user_type"
        )
        logger.info(f"Added {user_type} user {chat_id} ")

    def get_users_for_broadcast(self, user_type: str) -> List[str]:

        query = f"SELECT chat_id from {SCHEMA}.{TABLE} "
        if user_type != "all":
            query += f"where user_type = '{user_type}'"

        query_result = self._query(query)
        return [str(row[0]) for row in query_result]

    def get_user_type(self, chat_id: str) -> str:
        result = self._query(
            f"SELECT user_type from {SCHEMA}.{TABLE} where chat_id = '{chat_id}'"
        )[0][0]
        return str(result)

    def check_admin(self, chat_id: str) -> bool:
        result = self._query(
            f"select chat_id from {SCHEMA}.{ADMIN_TABLE} where chat_id = '{chat_id}' and is_active = true"
        )
        if len(result) > 0:
            return True
        return False

    def _query(self, query: str):

        try:
            return self._pg.query(query)
        except Exception as ex:
            logger.error(f"Insert failed: {str(ex)}")
            logger.error("Trying to re-init connection")
            self._pg: PostgresHandler = PostgresHandler()
            return self._pg.query(query)

    def _execute(self, query: str) -> None:

        try:
            self._pg.execute(query)
        except Exception as ex:
            logger.error(f"Insert failed: {str(ex)}")
            logger.error("Trying to re-init connection")
            self._pg: PostgresHandler = PostgresHandler()
            self._pg.execute(query)
