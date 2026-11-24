"""Проверки хранения данных."""

import json
from pathlib import Path

import pytest

from storage import load_data, save_data


def test_save_and_reload(tmp_path: Path) -> None:
    """Изменённые данные восстанавливаются из JSON."""
    path = tmp_path / "canteen.json"
    canteen = load_data(path)
    assert canteen.orders["Alice"].dish.name == "Pizza"
    canteen.add_user("Анна")
    canteen.add_order("Анна", "Soup")
    save_data(path, canteen)

    contents = json.loads(path.read_text(encoding="utf-8"))
    assert "Анна" in contents["users"]
    assert contents["menu"]["Soup"] == {"price": 4.5, "available": True}
    assert contents["orders"] == {"Alice": "Pizza", "Анна": "Soup"}

    loaded = load_data(path)
    order = loaded.orders["Анна"]
    assert order.visitor is loaded.visitors["Анна"]
    assert order.dish is loaded.menu["Soup"]
    assert loaded.order_statistics() == canteen.order_statistics()


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
