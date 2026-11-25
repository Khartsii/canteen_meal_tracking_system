CREATE TABLE IF NOT EXISTS visitors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL CHECK (price >= 0),
    available INTEGER NOT NULL CHECK (available IN (0, 1))
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    visitor_id INTEGER NOT NULL UNIQUE REFERENCES visitors(id),
    dish_id INTEGER NOT NULL REFERENCES dishes(id)
);

CREATE TABLE IF NOT EXISTS dish_unavailability (
    dish_id INTEGER NOT NULL REFERENCES dishes(id),
    unavailable_date TEXT NOT NULL,
    PRIMARY KEY (dish_id, unavailable_date)
);
