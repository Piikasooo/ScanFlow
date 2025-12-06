CREATE TABLE families (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'My Family',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY, -- ID від Telegram
    first_name TEXT,
    family_id UUID REFERENCES families(id) ON DELETE CASCADE, -- Зв'язок з сім'єю
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    icon TEXT -- Емодзі для краси в боті (🍔, 🚗)
);

-- Одразу наповнимо "Жорсткий список" (можете змінити під себе)
INSERT INTO categories (name, icon) VALUES
('Продукти', '🥦'),
('Кафе та Ресторани', '🍔'),
('Авто та Транспорт', '⛽'),
('Дім та Побут', '🏠'),
('Здоров''я', '💊'),
('Одяг та Взуття', '👕'),
('Техніка', '💻'),
('Розваги', '🎬'),
('Послуги', '💇'),
('Інше', '📦');

CREATE TABLE merchants (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE receipts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    family_id UUID REFERENCES families(id) NOT NULL, -- Головний власник чеку
    uploader_id BIGINT REFERENCES users(telegram_id), -- Хто завантажив
    merchant_id INT REFERENCES merchants(id),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'UAH',
    raw_text TEXT, -- Для відлагодження AI
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE receipt_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    receipt_id UUID REFERENCES receipts(id) ON DELETE CASCADE,
    category_id INT REFERENCES categories(id), -- Посилання на жорсткий список
    name TEXT NOT NULL,
    quantity DECIMAL(10, 3) DEFAULT 1,
    price DECIMAL(10, 2),
    total DECIMAL(10, 2)
);