CREATE TABLE IF NOT EXISTS vacancy_data (
    id SERIAL PRIMARY KEY,                    -- Внутренний ID
    name_vacancy VARCHAR(100),
    name_company VARCHAR(100),
    link TEXT UNIQUE,
    skills TEXT[],

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
