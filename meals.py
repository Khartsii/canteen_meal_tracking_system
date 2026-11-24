"""Операции с посетителями, блюдами и заказами."""

Dish = dict[str, float | bool]
Menu = dict[str, Dish]
Orders = dict[str, str]


def add_user(users: list[str], name: str) -> str:
    """Добавить посетителя или сообщить, что он уже зарегистрирован."""
    name = name.strip()
    if not name:
        raise ValueError("Введите имя посетителя.")
    if name in users:
        return f"{name} уже есть в списке посетителей."
    users.append(name)
    return f"{name} добавлен в список посетителей."


def dish_info(name: str, price: float, available: bool) -> str:
    """Показать цену и доступность блюда."""
    if available:
        return f"{name} доступно для заказа. Цена: ${price:.2f}."
    return f"{name} недоступно для заказа."


def info_user(name: str, users: list[str], orders: Orders) -> str:
    """Показать заказ посетителя."""
    if name not in users:
        return f"Посетитель {name} не найден."
    if name not in orders:
        return f"У посетителя {name} нет заказа."
    return f"Заказ посетителя {name}: {orders[name]}."


def add_order(
    users: list[str], menu: Menu, orders: Orders, user: str, dish: str,
) -> None:
    """Создать заказ на доступное блюдо для зарегистрированного посетителя."""
    if user not in users:
        raise ValueError("Посетитель не найден.")
    if dish not in menu:
        raise ValueError("Блюдо не найдено.")
    if not menu[dish]["available"]:
        raise ValueError("Блюдо недоступно.")
    if user in orders:
        raise ValueError("У посетителя уже есть заказ.")
    orders[user] = dish


def cancel_order(orders: Orders, user: str) -> None:
    """Отменить действующий заказ посетителя."""
    if user not in orders:
        raise ValueError("У посетителя нет заказа.")
    del orders[user]


def find_users(users: list[str], query: str) -> list[str]:
    """Найти посетителей по части имени и отсортировать результат."""
    matches = [name for name in users if query.casefold() in name.casefold()]
    return sorted(matches, key=str.casefold)


def order_statistics(menu: Menu, orders: Orders) -> tuple[int, float]:
    """Подсчитать действующие заказы и их общую стоимость."""
    total = sum(menu[name]["price"] for name in orders.values())
    return len(orders), float(total)
