"""Консольный интерфейс системы учёта питания."""

from argparse import ArgumentParser
from pathlib import Path

from meals import (
    add_order,
    add_user,
    cancel_order,
    dish_info,
    find_users,
    info_user,
    order_statistics,
)
from storage import Data, load_data, save_data

DATA_FILE = Path(__file__).with_name("canteen_data.json")

MENU = """
1. Добавить посетителя
2. Показать блюда
3. Посмотреть заказ посетителя
4. Оформить заказ
5. Отменить заказ
6. Найти посетителей
7. Показать статистику заказов
0. Выйти
"""


def read_name() -> str:
    """Запросить имя посетителя."""
    return input("Имя посетителя: ").strip()


def run_action(choice: str, data: Data, path: Path) -> None:
    """Выполнить выбранное действие и сохранить изменения."""
    users, menu, orders = data
    if choice == "1":
        updated_users = users.copy()
        message = add_user(updated_users, read_name())
        if updated_users != users:
            save_data(path, (updated_users, menu, orders))
            users[:] = updated_users
        print(message)
    elif choice == "2":
        for name in sorted(menu, key=str.casefold):
            dish = menu[name]
            print(dish_info(name, dish["price"], bool(dish["available"])))
    elif choice == "3":
        print(info_user(read_name(), users, orders))
    elif choice in ("4", "5"):
        user = read_name()
        updated_orders = orders.copy()
        if choice == "4":
            dish_name = input("Название блюда: ").strip()
            add_order(users, menu, updated_orders, user, dish_name)
            message = "Заказ оформлен."
        else:
            cancel_order(updated_orders, user)
            message = "Заказ отменён."
        save_data(path, (users, menu, updated_orders))
        orders.clear()
        orders.update(updated_orders)
        print(message)
    elif choice == "6":
        matches = find_users(users, input("Часть имени: ").strip())
        print(", ".join(matches) if matches else "Посетители не найдены.")
    elif choice == "7":
        count, total = order_statistics(menu, orders)
        print(f"Количество заказов: {count}. Стоимость: ${total:.2f}.")
    else:
        raise ValueError("Выберите пункт меню от 0 до 7.")


def main() -> int:
    """Загрузить данные и запустить меню или исходный сценарий."""
    parser = ArgumentParser(description="Система учёта питания в столовой")
    parser.add_argument("--demo", action="store_true", help="сценарий ПР №1")
    args = parser.parse_args()

    try:
        data = load_data(DATA_FILE)
    except (OSError, ValueError) as error:
        print(f"Не удалось загрузить данные: {error}")
        return 1

    try:
        if args.demo:
            run_action("1", data, DATA_FILE)
            users, menu, orders = data
            if "Pizza" in menu:
                pizza = menu["Pizza"]
                print(
                    dish_info(
                        "Pizza", pizza["price"], bool(pizza["available"]),
                    ),
                )
            print(info_user("Alice", users, orders))
            return 0

        while True:
            print(MENU)
            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return 0
            try:
                run_action(choice, data, DATA_FILE)
            except (ValueError, OSError) as error:
                print(f"Ошибка: {error}")
    except (EOFError, KeyboardInterrupt):
        print("\nРабота завершена.")
        return 0
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
