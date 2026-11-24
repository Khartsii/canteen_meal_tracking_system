"""Объекты столовой и операции с ними."""


class Visitor:
    """Посетитель столовой."""

    def __init__(self, name: str) -> None:
        """Сохранить имя посетителя."""
        self.name = name

    def __str__(self) -> str:
        """Вернуть имя посетителя."""
        return self.name


class Dish:
    """Блюдо из меню с ценой и признаком доступности."""

    def __init__(self, name: str, price: float, available: bool) -> None:
        """Запомнить данные блюда."""
        self.name = name
        self.price = price
        self.available = available

    def __str__(self) -> str:
        """Показать цену и доступность блюда."""
        if self.available:
            return f"{self.name} доступно для заказа. Цена: ${self.price:.2f}."
        return f"{self.name} недоступно для заказа."


class Order:
    """Действующий заказ посетителя на одно блюдо."""

    def __init__(self, visitor: Visitor, dish: Dish) -> None:
        """Связать посетителя и выбранное блюдо."""
        self.visitor = visitor
        self.dish = dish

    def __str__(self) -> str:
        """Сформировать описание заказа."""
        return f"Заказ посетителя {self.visitor}: {self.dish.name}."


class Canteen:
    """Коллекции посетителей, блюд и действующих заказов."""

    def __init__(
        self,
        visitors: dict[str, Visitor],
        menu: dict[str, Dish],
        orders: dict[str, Order],
    ) -> None:
        """Принять коллекции объектов столовой."""
        self.visitors = visitors
        self.menu = menu
        self.orders = orders

    def copy(self) -> "Canteen":
        """Скопировать коллекции для изменения перед записью на диск."""
        return Canteen(
            self.visitors.copy(), self.menu.copy(), self.orders.copy(),
        )

    def add_user(self, name: str) -> str:
        """Добавить посетителя или сообщить, что он уже зарегистрирован."""
        name = name.strip()
        if not name:
            raise ValueError("Введите имя посетителя.")
        if name in self.visitors:
            return f"{name} уже есть в списке посетителей."
        self.visitors[name] = Visitor(name)
        return f"{name} добавлен в список посетителей."

    def info_user(self, name: str) -> str:
        """Показать заказ посетителя."""
        if name not in self.visitors:
            return f"Посетитель {name} не найден."
        if name not in self.orders:
            return f"У посетителя {name} нет заказа."
        return str(self.orders[name])

    def add_order(self, user: str, dish: str) -> None:
        """Создать заказ на доступное блюдо."""
        if user not in self.visitors:
            raise ValueError("Посетитель не найден.")
        if dish not in self.menu:
            raise ValueError("Блюдо не найдено.")
        selected_dish = self.menu[dish]
        if not selected_dish.available:
            raise ValueError("Блюдо недоступно.")
        if user in self.orders:
            raise ValueError("У посетителя уже есть заказ.")
        self.orders[user] = Order(self.visitors[user], selected_dish)

    def cancel_order(self, user: str) -> None:
        """Отменить действующий заказ посетителя."""
        if user not in self.orders:
            raise ValueError("У посетителя нет заказа.")
        del self.orders[user]

    def find_users(self, query: str) -> list[Visitor]:
        """Найти посетителей по части имени и отсортировать результат."""
        query = query.casefold()
        matches = [
            visitor for visitor in self.visitors.values()
            if query in visitor.name.casefold()
        ]
        return sorted(matches, key=lambda visitor: visitor.name.casefold())

    def order_statistics(self) -> tuple[int, float]:
        """Подсчитать действующие заказы и их общую стоимость."""
        total = sum(order.dish.price for order in self.orders.values())
        return len(self.orders), float(total)
