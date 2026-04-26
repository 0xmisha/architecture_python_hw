-- ============================================================
-- Hotel Booking System — SQL Queries (Variant 13)
-- ============================================================

-- ------------------------------------------------------------
-- 1. Создание нового пользователя
-- ------------------------------------------------------------
INSERT INTO users (login, password_hash, first_name, last_name, email)
VALUES (
    'new_user',
    '$2b$12$...',   -- bcrypt hash
    'Новый',
    'Пользователь',
    'new_user@example.com'
)
RETURNING id, login, first_name, last_name, email;

-- ------------------------------------------------------------
-- 2. Поиск пользователя по логину (точное совпадение)
-- ------------------------------------------------------------
SELECT id, login, first_name, last_name, email
FROM users
WHERE login = 'ivan_petrov';

-- ------------------------------------------------------------
-- 3. Поиск пользователя по маске имя/фамилия (ILIKE)
-- ------------------------------------------------------------
SELECT id, login, first_name, last_name, email
FROM users
WHERE first_name ILIKE '%ван%'
   OR last_name  ILIKE '%ван%';

-- ------------------------------------------------------------
-- 4. Создание отеля
-- ------------------------------------------------------------
INSERT INTO hotels (name, city, address, stars, rooms_total, price_per_night)
VALUES (
    'Новый Отель',
    'Москва',
    'ул. Примерная, 1',
    4,
    100,
    7500.00
)
RETURNING id, name, city, address, stars, rooms_total, price_per_night;

-- ------------------------------------------------------------
-- 5. Получение списка всех отелей
-- ------------------------------------------------------------
SELECT id, name, city, address, stars, rooms_total, price_per_night
FROM hotels
ORDER BY city, name;

-- ------------------------------------------------------------
-- 6. Поиск отелей по городу (ILIKE)
-- ------------------------------------------------------------
SELECT id, name, city, address, stars, rooms_total, price_per_night
FROM hotels
WHERE city ILIKE '%осква%'
ORDER BY stars DESC, price_per_night;

-- ------------------------------------------------------------
-- 7. Создание бронирования
-- ------------------------------------------------------------
INSERT INTO bookings (user_id, hotel_id, check_in, check_out, total_price, status)
VALUES (
    '11111111-0000-0000-0000-000000000001',
    '22222222-0000-0000-0000-000000000003',
    '2026-02-01',
    '2026-02-05',
    -- total_price = nights * price_per_night
    (SELECT price_per_night * ('2026-02-05'::date - '2026-02-01'::date)
     FROM hotels WHERE id = '22222222-0000-0000-0000-000000000003'),
    'confirmed'
)
RETURNING *;

-- ------------------------------------------------------------
-- 8. Получение бронирований пользователя
-- ------------------------------------------------------------
SELECT
    b.id,
    b.user_id,
    b.hotel_id,
    h.name  AS hotel_name,
    b.check_in,
    b.check_out,
    b.total_price,
    b.status,
    b.created_at
FROM bookings b
JOIN hotels h ON h.id = b.hotel_id
WHERE b.user_id = '11111111-0000-0000-0000-000000000001'
ORDER BY b.created_at DESC;

-- ------------------------------------------------------------
-- 9. Отмена бронирования
-- ------------------------------------------------------------
UPDATE bookings
SET status = 'cancelled'
WHERE id      = '33333333-0000-0000-0000-000000000001'
  AND user_id = '11111111-0000-0000-0000-000000000001'
  AND status  = 'confirmed'
RETURNING id, status;

-- ------------------------------------------------------------
-- 10. Получение бронирования по id (+ владелец-проверка)
-- ------------------------------------------------------------
SELECT
    b.id,
    b.user_id,
    b.hotel_id,
    h.name  AS hotel_name,
    b.check_in,
    b.check_out,
    b.total_price,
    b.status,
    b.created_at
FROM bookings b
JOIN hotels h ON h.id = b.hotel_id
WHERE b.id      = '33333333-0000-0000-0000-000000000003'
  AND b.user_id = '11111111-0000-0000-0000-000000000002';

-- ------------------------------------------------------------
-- 11. Аналитика: количество активных бронирований по городу
-- ------------------------------------------------------------
SELECT
    h.city,
    COUNT(b.id)         AS active_bookings,
    SUM(b.total_price)  AS total_revenue
FROM bookings b
JOIN hotels h ON h.id = b.hotel_id
WHERE b.status = 'confirmed'
GROUP BY h.city
ORDER BY total_revenue DESC;

-- ------------------------------------------------------------
-- 12. Проверка доступности отеля на даты (нет пересечений)
-- ------------------------------------------------------------
SELECT COUNT(*) = 0 AS is_available
FROM bookings
WHERE hotel_id  = '22222222-0000-0000-0000-000000000001'
  AND status    = 'confirmed'
  AND check_in  < '2026-02-10'::date
  AND check_out > '2026-02-05'::date;
