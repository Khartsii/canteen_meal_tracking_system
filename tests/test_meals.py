"""Проверки объектов и операций учёта питания."""

import pytest

from meals import Canteen, Dish, Visitor


@pytest.fixture
def canteen() -> Canteen:
    """Создать столовую с посетителями и двумя блюдами."""
    visitors = {name: Visitor(name) for name in ("Charlie", "Bob", "Alice")}
    menu = {
        "Pizza": Dish("Pizza", 10.99, True),
        "Salad": Dish("Salad", 5.0, False),
    }
    return Canteen(visitors, menu, {})


def test_add_user_and_duplicate(canteen: Canteen) -> None:
    """Имя очищается от пробелов, дубликат не заменяет посетителя."""
    canteen.add_user("  Eve  ")
    visitor = canteen.visitors["Eve"]
    assert "уже есть" in canteen.add_user("Eve")
    assert canteen.visitors["Eve"] is visitor
    assert str(visitor) == "Eve"


def test_reject_empty_name(canteen: Canteen) -> None:
    """Имя из одних пробелов недопустимо."""
    with pytest.raises(ValueError, match="Введите имя"):
        canteen.add_user(" ")


def test_dish_info(canteen: Canteen) -> None:
    """Цена показана для доступного блюда."""
    assert "$10.99" in str(canteen.menu["Pizza"])
    assert "недоступно" in str(canteen.menu["Salad"])


def test_view_order(canteen: Canteen) -> None:
    """Просмотр различает существующий заказ и его отсутствие."""
    canteen.add_order("Alice", "Pizza")
    assert canteen.info_user("Alice") == "Заказ посетителя Alice: Pizza."
    assert "нет заказа" in canteen.info_user("Bob")
    assert "не найден" in canteen.info_user("Eve")


def test_order_and_cancellation(canteen: Canteen) -> None:
    """Заказ связывает объекты посетителя и блюда и учитывается в итогах."""
    canteen.add_order("Alice", "Pizza")
    order = canteen.orders["Alice"]
    assert order.visitor is canteen.visitors["Alice"]
    assert order.dish is canteen.menu["Pizza"]
    assert canteen.order_statistics() == (1, 10.99)
    with pytest.raises(ValueError, match="уже есть заказ"):
        canteen.add_order("Alice", "Pizza")
    canteen.cancel_order("Alice")
    assert canteen.order_statistics() == (0, 0.0)
    with pytest.raises(ValueError, match="нет заказа"):
        canteen.cancel_order("Alice")


def test_reject_unavailable_dish(canteen: Canteen) -> None:
    """Оформление недоступного блюда не меняет заказы."""
    with pytest.raises(ValueError, match="Блюдо недоступно"):
        canteen.add_order("Alice", "Salad")
    assert canteen.orders == {}


def test_search_and_sort_users(canteen: Canteen) -> None:
    """Поиск возвращает объекты по части имени без учёта регистра."""
    assert canteen.find_users("LI") == [
        canteen.visitors["Alice"],
        canteen.visitors["Charlie"],
    ]
