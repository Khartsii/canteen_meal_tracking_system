-- query: dishes
-- Полное меню.
SELECT name, price, available
FROM dishes
ORDER BY name COLLATE NOCASE;

-- query: visitors
-- Список зарегистрированных посетителей.
SELECT name
FROM visitors
ORDER BY name COLLATE NOCASE;

-- query: dish_detail
-- Карточка блюда. Параметр — название блюда.
SELECT name, price, available
FROM dishes
WHERE name = ?;

-- query: available_dishes
-- Доступные блюда на дату. Параметр — дата YYYY-MM-DD.
SELECT dishes.name, dishes.price, dishes.available
FROM dishes
WHERE dishes.available = 1
  AND NOT EXISTS (
      SELECT 1
      FROM dish_unavailability
      WHERE dish_unavailability.dish_id = dishes.id
        AND dish_unavailability.unavailable_date = ?
  )
ORDER BY dishes.name COLLATE NOCASE;

-- query: orders
-- Действующие заказы с именами посетителей и блюдами.
SELECT visitors.name AS visitor, dishes.name AS dish, dishes.price
FROM orders
JOIN visitors ON visitors.id = orders.visitor_id
JOIN dishes ON dishes.id = orders.dish_id
ORDER BY orders.id;

-- query: order_detail
-- Карточка заказа. Параметр — имя посетителя.
SELECT visitors.name AS visitor, dishes.name AS dish, dishes.price
FROM orders
JOIN visitors ON visitors.id = orders.visitor_id
JOIN dishes ON dishes.id = orders.dish_id
WHERE visitors.name = ?;

-- query: order_totals
-- Число и суммарная стоимость заказов.
SELECT COUNT(*) AS count, COALESCE(SUM(dishes.price), 0) AS total
FROM orders
JOIN dishes ON dishes.id = orders.dish_id;

-- query: price_summary
-- Границы цен и средняя цена по меню.
SELECT MIN(price) AS minimum, MAX(price) AS maximum, AVG(price) AS average
FROM dishes;

-- query: dish_counts
-- Число блюд в группах доступности.
SELECT available, COUNT(*) AS count
FROM dishes
GROUP BY available
ORDER BY available DESC;

-- query: ordered_dishes
-- Количество заказов по каждому заказанному блюду.
SELECT dishes.name, COUNT(orders.id) AS count
FROM dishes
LEFT JOIN orders ON orders.dish_id = dishes.id
GROUP BY dishes.id, dishes.name
HAVING COUNT(orders.id) > 0
ORDER BY count DESC, dishes.name COLLATE NOCASE;
