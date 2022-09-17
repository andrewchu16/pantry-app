DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS storages;
DROP TABLE IF EXISTS items;

-- Pantry users
CREATE TABLE users (
    user_id integer PRIMARY KEY AUTOINCREMENT,
    username text,
    hash text
);

-- user grocery lists and pantry
CREATE TABLE storages (
    storage_id integer PRIMARY KEY AUTOINCREMENT,
    storage_type integer, -- 0 means grocery list, 1 means pantry
    user_id integer,
    storage_name text
);

-- grocery items
CREATE TABLE lists (
    item_id integer PRIMARY KEY AUTOINCREMENT,
    storage_id integer,
    item_name text,
    price real,
    purchase_date DATETIME,
    expiry_date DATETIME
);
