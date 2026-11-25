"""Проверки импорта и ограничений SQLite."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from db.database import connect
from db.import_json import import_data
from storage import STARTER_FILE


def test_import_can_be_repeated(tmp_path: Path) -> None:
    """Повторный импорт сохраняет справочники и обновляет заказы."""
    path = tmp_path / "canteen.sqlite3"
    assert import_data(STARTER_FILE, path) == (5, 3, 1)
    assert import_data(STARTER_FILE, path) == (5, 3, 1)
    with closing(connect(path)) as connection:
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        row = connection.execute(
            "SELECT visitors.name AS visitor, dishes.name AS dish "
            "FROM orders JOIN visitors ON visitors.id = orders.visitor_id "
            "JOIN dishes ON dishes.id = orders.dish_id",
        ).fetchone()
        assert isinstance(row, sqlite3.Row)
        assert row["visitor"] == "Alice"
        assert row["dish"] == "Pizza"
        count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()
        assert count[0] == 1


def test_foreign_keys_are_enforced(tmp_path: Path) -> None:
    """Запись заказа с неизвестными ключами отклоняется."""
    path = tmp_path / "canteen.sqlite3"
    import_data(STARTER_FILE, path)
    with closing(connect(path)) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO orders (visitor_id, dish_id) VALUES (?, ?)",
                (999, 999),
            )
