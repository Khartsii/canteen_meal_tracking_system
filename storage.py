"""Чтение и запись данных столовой в JSON."""

import json
from math import isfinite
from pathlib import Path
from tempfile import TemporaryDirectory

from meals import Canteen, Dish, Order, Visitor

DATA_FILE = Path(__file__).with_name("canteen_data.json")
STARTER_FILE = Path(__file__).with_name("initial_data.json")


def load_data(path: Path) -> Canteen:
    """Прочитать данные проекта или загрузить начальный набор."""
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        with STARTER_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("В JSON ожидается объект с данными столовой.")

    users = data.get("users")
    menu = data.get("menu")
    orders = data.get("orders")
    if not isinstance(users, list) or not all(
        isinstance(name, str) and name.strip() for name in users
    ):
        raise ValueError("В JSON требуется список имён посетителей.")
    if len(users) != len(set(users)):
        raise ValueError("В JSON найдены повторяющиеся имена посетителей.")
    if not isinstance(menu, dict):
        raise ValueError("В JSON требуется словарь блюд.")
    dishes: dict[str, Dish] = {}
    for name, dish in menu.items():
        if not isinstance(dish, dict):
            raise ValueError("Описание блюда должно быть объектом.")
        price = dish.get("price")
        available = dish.get("available")
        if (
            type(price) not in (int, float)
            or price < 0
            or (isinstance(price, float) and not isfinite(price))
            or not isinstance(available, bool)
        ):
            raise ValueError("Проверьте цену и доступность блюд в JSON.")
        dishes[name] = Dish(name, price, available)
    visitors = {name: Visitor(name) for name in users}
    if not isinstance(orders, dict) or not all(
        user in visitors and isinstance(dish, str) and dish in dishes
        for user, dish in orders.items()
    ):
        raise ValueError(
            "Заказы в JSON должны ссылаться на посетителей и блюда.",
        )
    loaded_orders = {
        name: Order(visitors[name], dishes[dish])
        for name, dish in orders.items()
    }
    return Canteen(visitors, dishes, loaded_orders)


def save_data(path: Path, data: Canteen) -> None:
    """Записать данные и заменить файл после успешной записи."""
    contents = {
        "users": [visitor.name for visitor in data.visitors.values()],
        "menu": {
            dish.name: {"price": dish.price, "available": dish.available}
            for dish in data.menu.values()
        },
        "orders": {
            order.visitor.name: order.dish.name
            for order in data.orders.values()
        },
    }
    with TemporaryDirectory(dir=path.parent) as directory:
        temp_path = Path(directory) / path.name
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temp_path.replace(path)
