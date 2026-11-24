"""Проверки функций учёта питания."""

import pytest

from meals import (
    add_order,
    add_user,
    cancel_order,
    dish_info,
    find_users,
    info_user,
    order_statistics,
)


def test_add_user_and_duplicate() -> None:
    """Имя очищается от пробелов, дубликат не добавляется."""
    users = ["Alice"]
    add_user(users, "  Bob  ")
    assert "уже есть" in add_user(users, "Bob")
    assert users == ["Alice", "Bob"]


def test_reject_empty_name() -> None:
    """Имя из одних пробелов недопустимо."""
    with pytest.raises(ValueError, match="Введите имя"):
        add_user([], " ")


def test_dish_info() -> None:
    """Цена показана для доступного блюда."""
    assert "$10.99" in dish_info("Pizza", 10.99, True)
    assert "недоступно" in dish_info("Salad", 5.0, False)


def test_view_order() -> None:
    """Просмотр различает существующий заказ и его отсутствие."""
    users = ["Alice", "Bob"]
    orders = {"Alice": "Pizza"}
    assert "Pizza" in info_user("Alice", users, orders)
    assert "нет заказа" in info_user("Bob", users, orders)
    assert "не найден" in info_user("Eve", users, orders)


def test_order_and_cancellation() -> None:
    """Заказ появляется в статистике и удаляется при отмене."""
    menu = {"Pizza": {"price": 10.99, "available": True}}
    orders: dict[str, str] = {}
    add_order(["Alice"], menu, orders, "Alice", "Pizza")
    assert order_statistics(menu, orders) == (1, 10.99)
    with pytest.raises(ValueError, match="уже есть заказ"):
        add_order(["Alice"], menu, orders, "Alice", "Pizza")
    cancel_order(orders, "Alice")
    assert order_statistics(menu, orders) == (0, 0.0)
    with pytest.raises(ValueError, match="нет заказа"):
        cancel_order(orders, "Alice")


def test_reject_unavailable_dish() -> None:
    """Оформление недоступного блюда не меняет заказы."""
    menu = {"Salad": {"price": 5.0, "available": False}}
    orders: dict[str, str] = {}
    with pytest.raises(ValueError, match="Блюдо недоступно"):
        add_order(["Alice"], menu, orders, "Alice", "Salad")
    assert orders == {}


def test_search_and_sort_users() -> None:
    """Поиск работает по части имени без учёта регистра."""
    assert find_users(["Charlie", "Bob", "Alice"], "LI") == [
        "Alice",
        "Charlie",
    ]
