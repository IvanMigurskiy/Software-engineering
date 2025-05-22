-- Подключение к базе данных (уже создана через POSTGRES_DB)
-- \c budget_tracker; -- Эта строка не нужна в Docker, так как скрипт выполняется в контексте указанной базы

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('client', 'admin')),
    hashed_password VARCHAR(255) NOT NULL,
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индекса для поиска по username
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_username') THEN
        CREATE INDEX idx_users_username ON users (username);
    END IF;
END $$;

-- Создание таблицы доходов
CREATE TABLE IF NOT EXISTS incomes (
    income_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    value INTEGER NOT NULL,
    due_date DATE,
    periodicity VARCHAR(20) NOT NULL CHECK (periodicity IN ('once', 'daily', 'weekly', 'monthly')),
    periodicity_value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

-- Создание индексов для поиска по статусу и периодичности
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_incomes_periodicity') THEN
        CREATE INDEX idx_incomes_periodicity ON incomes (periodicity);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_incomes_user_id') THEN
        CREATE INDEX idx_incomes_user_id ON incomes (user_id);
    END IF;
END $$;

-- Создание таблицы расходов
CREATE TABLE IF NOT EXISTS costs (
    cost_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    value INTEGER NOT NULL,
    due_date DATE,
    periodicity VARCHAR(20) NOT NULL CHECK (periodicity IN ('once', 'daily', 'weekly', 'monthly')),
    periodicity_value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

-- Создание индексов для поиска по статусу и периодичности
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_costs_periodicity') THEN
        CREATE INDEX idx_costs_periodicity ON costs (periodicity);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_costs_user_id') THEN
        CREATE INDEX idx_costs_user_id ON costs (user_id);
    END IF;
END $$;

-- Вставка тестовых данных (мастер-пользователь), если он еще не существует
INSERT INTO users (username, full_name, role, hashed_password)
SELECT 'admin', 'Master Administrator', 'admin', '$2b$12$C4e8jcxuZjpVAdTJ5IFQiOIOnRX1bTCNO/IN1Xa9Bn0GQXZuskFLC'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- Вставка тестового дохода, если он еще не существует
INSERT INTO incomes (title, due_date, value, periodicity, periodicity_value, user_id)
SELECT 'Тестовый доход', '2025-04-15', 10000, 'once', 0, 1
WHERE NOT EXISTS (SELECT 1 FROM incomes WHERE title = 'Тестовый доход');

-- Вставка тестового расхода, если он еще не существует
INSERT INTO costs (title, due_date, value, periodicity, periodicity_value, user_id)
SELECT 'Тестовый расход',  '2025-04-15', 10000, 'once', 0, 1
WHERE NOT EXISTS (SELECT 1 FROM costs WHERE title = 'Тестовый расход');

