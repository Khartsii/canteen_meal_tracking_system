"""Проверки маршрутов и страниц Django."""

from contextlib import closing
from pathlib import Path

import django
import pytest
from django.contrib.staticfiles.finders import find
from django.test import Client
from django.urls import reverse

from db import database
from db.import_json import import_data
from storage import load_data, save_data


@pytest.fixture
def client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> Client:
    """Запустить Django с временной SQLite, заполненной из JSON."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "canteen_web.settings")
    django.setup()
    path = tmp_path / "canteen.json"
    canteen = load_data(path)
    canteen.add_user("Анна")
    canteen.add_order("Анна", "Soup")
    save_data(path, canteen)
    db_path = tmp_path / "canteen.sqlite3"
    import_data(path, db_path)
    monkeypatch.setattr(database, "DB_PATH", db_path)
    return Client(HTTP_HOST="localhost")


def test_home_navigation(client: Client) -> None:
    """Главная страница содержит ссылки на меню и заказы."""
    response = client.get("/")
    assert response.status_code == 200
    content = response.content.decode()
    assert 'href="/menu/"' in content
    assert 'href="/orders/"' in content


def test_menu_and_dish(client: Client) -> None:
    """Меню ведёт на динамическую страницу блюда с ценой и доступностью."""
    url = reverse("menu:detail", kwargs={"name": "Pizza"})
    menu = client.get("/menu/")
    assert menu.status_code == 200
    assert f'href="{url}"' in menu.content.decode()

    dish = client.get(url)
    assert dish.status_code == 200
    assert "10,99" in dish.content.decode()
    assert "Доступно для заказа" in dish.content.decode()

    unavailable = client.get("/menu/Salad/")
    assert unavailable.status_code == 200
    assert "Недоступно для заказа" in unavailable.content.decode()


def test_orders_use_saved_data(client: Client) -> None:
    """Страница заказов показывает записи и сумму из JSON."""
    response = client.get("/orders/")
    assert response.status_code == 200
    content = response.content.decode()
    assert "Анна" in content
    assert "Soup" in content
    assert "Всего: 2. Общая стоимость: 15,49 $." in content


@pytest.mark.parametrize(
    "url", ["/unknown/", "/menu/unknown/", "/orders/unknown/"],
)
def test_not_found(client: Client, url: str) -> None:
    """Неизвестные путь, блюдо и заказ возвращают страницу 404."""
    response = client.get(url)
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()


def test_order_detail(client: Client) -> None:
    """Список ведёт на карточку заказа, сохранённого в JSON."""
    url = reverse("orders:detail", kwargs={"visitor": "Анна"})
    order_list = client.get(reverse("orders:list")).content.decode()
    assert f'href="{url}"' in order_list

    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Заказ посетителя Анна" in content
    assert "Soup" in content
    assert "4,50 $" in content
    assert "Действующий" in content
    assert 'href="/orders/"' in content


def test_empty_menu_and_orders(client: Client) -> None:
    """Пустые коллекции показывают сообщения на обеих страницах."""
    with closing(database.connect()) as connection, connection:
        connection.execute("DELETE FROM orders")
        connection.execute("DELETE FROM dishes")
    menu = client.get(reverse("menu:list"))
    assert menu.status_code == 200
    assert "Позиций в меню: 0" in menu.content.decode()
    assert "В меню пока нет блюд." in menu.content.decode()

    orders = client.get(reverse("orders:list"))
    assert orders.status_code == 200
    assert "Действующих заказов пока нет." in orders.content.decode()


def test_static_assets(client: Client) -> None:
    """Общий шаблон ссылается на найденные Django локальные файлы."""
    content = client.get(reverse("homepage:index")).content.decode()
    for asset in (
        "homepage/css/site.css",
        "homepage/img/logo.png",
        "homepage/js/site.js",
    ):
        assert f'"/static/{asset}"' in content
        assert find(asset) is not None


def test_availability_by_date(client: Client) -> None:
    """На выбранную дату учитываются исключения из доступного меню."""
    with closing(database.connect()) as connection, connection:
        connection.execute(
            "INSERT INTO dish_unavailability (dish_id, unavailable_date) "
            "SELECT id, ? FROM dishes WHERE name = ?",
            ("2026-11-25", "Pizza"),
        )

    url = reverse("menu:list")
    response = client.get(url, {"date": "2026-11-25"})
    assert response.status_code == 200
    assert "/menu/Soup/" in response.content.decode()
    assert "/menu/Pizza/" not in response.content.decode()
    assert "/menu/Salad/" not in response.content.decode()
    other_date = client.get(url, {"date": "2026-11-26"})
    assert "/menu/Pizza/" in other_date.content.decode()
    assert client.get(url, {"date": "2026-11-31"}).status_code == 400


def test_statistics(client: Client) -> None:
    """Статистика отображает агрегаты и группы из SQLite."""
    response = client.get(reverse("homepage:statistics"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Посетителей: 6." in content
    assert "Действующих заказов: 2." in content
    assert "Доступно: 2" in content
    assert "Недоступно: 1" in content
    assert "Pizza: 1" in content
    assert "Salad: 0" not in content
