"""Перенос данных консольной версии из JSON в SQLite."""

from argparse import ArgumentParser
from contextlib import closing
from pathlib import Path

from storage import DATA_FILE, load_data

from .database import DB_PATH, SQL_DIR, connect


def import_data(source: Path, destination: Path) -> tuple[int, int, int]:
    """Загрузить JSON, обновить справочники и заменить список заказов."""
    canteen = load_data(source)
    schema = (SQL_DIR / "schema.sql").read_text(encoding="utf-8")

    with closing(connect(destination)) as connection:
        connection.executescript(schema)
        with connection:
            connection.executemany(
                "INSERT INTO visitors (name) VALUES (?) "
                "ON CONFLICT (name) DO NOTHING",
                ((name,) for name in canteen.visitors),
            )
            connection.executemany(
                "INSERT INTO dishes (name, price, available) VALUES (?, ?, ?) "
                "ON CONFLICT (name) DO UPDATE SET "
                "price = excluded.price, available = excluded.available",
                (
                    (dish.name, dish.price, dish.available)
                    for dish in canteen.menu.values()
                ),
            )
            visitor_ids = {
                row["name"]: row["id"]
                for row in connection.execute(
                    "SELECT id, name FROM visitors",
                )
            }
            dish_ids = {
                row["name"]: row["id"]
                for row in connection.execute("SELECT id, name FROM dishes")
            }
            connection.execute("DELETE FROM orders")
            connection.executemany(
                "INSERT INTO orders (visitor_id, dish_id) VALUES (?, ?)",
                (
                    (
                        visitor_ids[order.visitor.name],
                        dish_ids[order.dish.name],
                    )
                    for order in canteen.orders.values()
                ),
            )

    return len(canteen.visitors), len(canteen.menu), len(canteen.orders)


def main() -> None:
    """Перенести данные из рабочего JSON или начального набора."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--database", type=Path, default=DB_PATH)
    args = parser.parse_args()
    if args.source is not None and not args.source.is_file():
        parser.error("Указанный JSON-файл не найден.")
    visitors, dishes, orders = import_data(
        args.source or DATA_FILE, args.database,
    )
    print(
        f"Импортировано: посетителей {visitors}, "
        f"блюд {dishes}, заказов {orders}.",
    )


if __name__ == "__main__":
    main()
