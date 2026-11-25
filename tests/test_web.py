"""Проверки маршрутов и страниц Django."""

from datetime import date
from pathlib import Path

import pytest
from django.contrib.staticfiles.finders import find
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from db.import_json import import_data
from menu.models import Dish, DishUnavailability
from orders.models import Order, Visitor
from storage import load_data, save_data


@pytest.fixture
def client(
    tmp_path: Path, db: None,
) -> Client:
    """Запустить Django с временной SQLite, заполненной из JSON."""
    path = tmp_path / "canteen.json"
    canteen = load_data(path)
    canteen.add_user("Анна")
    canteen.add_order("Анна", "Soup")
    save_data(path, canteen)
    db_path = tmp_path / "canteen.sqlite3"
    import_data(path, db_path)
    call_command("import_pr7", source=db_path)
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
    url = reverse("menu:detail", kwargs={"slug": "pizza"})
    menu = client.get("/menu/")
    assert menu.status_code == 200
    assert f'href="{url}"' in menu.content.decode()

    dish = client.get(url)
    assert dish.status_code == 200
    assert "10,99" in dish.content.decode()
    assert "Доступно для заказа" in dish.content.decode()

    unavailable = client.get("/menu/dish/salad/")
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
    Order.objects.all().delete()
    Dish.objects.all().delete()
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
    DishUnavailability.objects.create(
        dish=Dish.objects.get(name="Pizza"),
        unavailable_date=date(2026, 11, 25),
    )

    url = reverse("menu:list")
    response = client.get(url, {"date": "2026-11-25"})
    assert response.status_code == 200
    assert "/menu/dish/soup/" in response.content.decode()
    assert "/menu/dish/pizza/" not in response.content.decode()
    assert "/menu/dish/salad/" not in response.content.decode()
    other_date = client.get(url, {"date": "2026-11-26"})
    assert "/menu/dish/pizza/" in other_date.content.decode()
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


def test_orders_filters_and_pagination(client: Client) -> None:
    """Параметры поиска, фильтра и сортировки сохраняются между страницами."""
    pizza = Dish.objects.get(name="Pizza")
    for number in range(7):
        visitor = Visitor.objects.create(name=f"Посетитель {number}")
        Order.objects.create(visitor=visitor, dish=pizza)

    url = reverse("orders:list")
    parameters = {"q": "Pizza", "dish": "Pizza", "sort": "visitor"}
    first = client.get(url, parameters).content.decode()
    assert "Страница 1 из 2" in first
    assert "Всего: 8" in first
    assert "q=Pizza&amp;dish=Pizza&amp;sort=visitor&amp;page=2" in first
    assert "Посетитель 0" in first
    assert "Посетитель 6" not in first
    assert "Soup" in first  # Доступен в списке вариантов фильтра.
    assert "Анна" not in first

    second = client.get(url, {**parameters, "page": 2}).content.decode()
    assert "Страница 2 из 2" in second
    assert "Посетитель 6" in second
    invalid = client.get(url, {"sort": "unknown", "page": "bad"})
    assert invalid.status_code == 200


def test_dish_search_combines_with_date(client: Client) -> None:
    """Поиск по названию можно сочетать с фильтром доступности."""
    url = reverse("menu:list")
    response = client.get(url, {"q": "pIz", "date": "2026-11-25"})
    assert response.status_code == 200
    assert 'href="/menu/dish/pizza/"' in response.content.decode()
    assert 'href="/menu/dish/soup/"' not in response.content.decode()


def test_portions_and_order_statuses(client: Client) -> None:
    """На выбранную дату остаток уменьшают только действующие заказы."""
    pizza = Dish.objects.get(name="Pizza")
    pizza.daily_portions = 1
    pizza.save(update_fields=["daily_portions"])
    day = date(2026, 11, 25)
    active = Order.objects.get(visitor__name="Alice")
    active.meal_date = day
    active.save(update_fields=["meal_date"])
    finished = Order.objects.create(
        visitor=active.visitor,
        dish=pizza,
        meal_date=day,
        status=Order.Status.COMPLETED,
    )

    menu_url = reverse("menu:list")
    assert pizza.get_absolute_url() not in client.get(
        menu_url, {"date": day.isoformat()},
    ).content.decode()
    active.status = Order.Status.CANCELLED
    active.save(update_fields=["status"])
    assert pizza.get_absolute_url() in client.get(
        menu_url, {"date": day.isoformat()},
    ).content.decode()

    orders_url = reverse("orders:list")
    content = client.get(
        orders_url,
        {"status": Order.Status.COMPLETED, "date": day.isoformat()},
    ).content.decode()
    assert reverse("orders:by_id", kwargs={"pk": finished.pk}) in content
    assert reverse("orders:by_id", kwargs={"pk": active.pk}) not in content
    stats = client.get(reverse("homepage:statistics")).content.decode()
    assert "Действующие: 1" in stats
    assert "Отменённые: 1" in stats
    assert "Выполненные: 1" in stats


def test_admin_orders(client: Client, django_user_model: type) -> None:
    """Администратор видит связанные записи и может искать по имени."""
    admin_user = django_user_model.objects.create_superuser(
        username="tester", password=None,
    )
    client.force_login(admin_user)
    response = client.get(
        reverse("admin:orders_order_changelist"),
        {"q": "Alice", "status__exact": Order.Status.ACTIVE},
    )
    assert response.status_code == 200
    assert "Alice" in response.content.decode()
    assert "Pizza" in response.content.decode()
    result_list = response.context["cl"].result_list
    assert [order.visitor.name for order in result_list] == ["Alice"]
