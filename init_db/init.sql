CREATE TABLE IF NOT EXISTS vacancy_data (
    id SERIAL PRIMARY KEY,                    -- Внутренний ID
    id_vacancy BIGINT UNIQUE,
    name_vacancy VARCHAR(255),
    name_company VARCHAR(255),
    link TEXT UNIQUE,
    skills TEXT[],

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_id_vacancy ON vacancy_data (id_vacancy);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    url TEXT DEFAULT 'https://abakan.hh.ru/search/vacancy?text=python',
    telegram_id BIGINT UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO users (url, telegram_id)
VALUES ('https://abakan.hh.ru/search/vacancy?text=playwright&work_format=REMOTE&items_on_page=20&&experience=moreThan6', 5103681164);
