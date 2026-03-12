DROP TABLE IF EXISTS contacts;

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL
        CHECK (
            btrim(full_name) <> ''
            AND full_name ~ '^[A-Za-zА-Яа-яЁё'' -]+$'
            AND full_name !~ '[0-9]'
        ),
    phone VARCHAR(20) NOT NULL
        CHECK (
            phone ~ '^\+?[0-9]{11}$'
        ),
    note TEXT
);