"""Проверки хранения данных."""

import json
from pathlib import Path

import pytest

from storage import load_data, save_data


def test_save_and_reload(tmp_path: Path) -> None:
    """Изменённые данные восстанавливаются из JSON."""
    path = tmp_path / "canteen.json"
    users, menu, orders = load_data(path)
    assert orders["Alice"] == "Pizza"
    users.append("Анна")
    orders["Анна"] = "Soup"
    save_data(path, (users, menu, orders))
    assert load_data(path) == (users, menu, orders)
    assert "Анна" in path.read_text(encoding="utf-8")


def test_reject_malformed_json(tmp_path: Path) -> None:
    """Повреждённый JSON вызывает исключение и остаётся на диске."""
    path = tmp_path / "canteen.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_data(path)
    assert path.read_text(encoding="utf-8") == "{"


def test_reject_order_with_unknown_dish(tmp_path: Path) -> None:
    """Заказ должен ссылаться на блюдо из меню."""
    path = tmp_path / "canteen.json"
    path.write_text(
        '{"users": ["Alice"], "menu": {}, "orders": {"Alice": "Pizza"}}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Заказы в JSON"):
        load_data(path)
