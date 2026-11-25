"""Подключение к SQLite и чтение запросов проекта."""

import sqlite3
from contextlib import closing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "canteen.sqlite3"
SQL_DIR = BASE_DIR / "sql"


def connect(path: Path | None = None) -> sqlite3.Connection:
    """Открыть базу с именованными строками и контролем внешних ключей."""
    connection = sqlite3.connect(DB_PATH if path is None else path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def load_queries() -> dict[str, str]:
    """Прочитать именованные SQL-запросы из файла для CLI и Django."""
    source = (SQL_DIR / "queries.sql").read_text(encoding="utf-8")
    return {
        name: query for name, query in (
            block.split("\n", 1) for block in source.split("-- query: ")[1:]
        )
    }


QUERIES = load_queries()


def select(name: str, *parameters: str) -> list[sqlite3.Row]:
    """Выполнить запрос чтения с параметрами и закрыть соединение."""
    with closing(connect()) as connection:
        return connection.execute(QUERIES[name], parameters).fetchall()
