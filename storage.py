"""Чтение и запись данных столовой в JSON."""

import json
from math import isfinite
from pathlib import Path
from tempfile import TemporaryDirectory

from meals import Menu, Orders

Data = tuple[list[str], Menu, Orders]
STARTER_FILE = Path(__file__).with_name("initial_data.json")


def load_data(path: Path) -> Data:
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
    for dish in menu.values():
        if not isinstance(dish, dict):
            raise ValueError("Описание блюда должно быть объектом.")
        price = dish.get("price")
        if (
            type(price) not in (int, float)
            or price < 0
            or (isinstance(price, float) and not isfinite(price))
            or not isinstance(dish.get("available"), bool)
        ):
            raise ValueError("Проверьте цену и доступность блюд в JSON.")
    if not isinstance(orders, dict) or not all(
        user in users and isinstance(dish, str) and dish in menu
        for user, dish in orders.items()
    ):
        raise ValueError(
            "Заказы в JSON должны ссылаться на посетителей и блюда.",
        )
    return users, menu, orders


def save_data(path: Path, data: Data) -> None:
    """Записать данные и заменить файл после успешной записи."""
    users, menu, orders = data
    contents = {"users": users, "menu": menu, "orders": orders}
    with TemporaryDirectory(dir=path.parent) as directory:
        temp_path = Path(directory) / path.name
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temp_path.replace(path)
