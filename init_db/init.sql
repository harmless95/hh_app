CREATE TABLE IF NOT EXISTS vacancy_data (
    id SERIAL PRIMARY KEY,                    -- Внутренний ID    name_vacancy VARCHAR(100),
    id_vacancy BIGINT UNIQUE,
    name_vacancy VARCHAR(100),
    name_company VARCHAR(100),
    link TEXT UNIQUE,
    skills TEXT[],

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_id_vacancy ON vacancy_data (id_vacancy);