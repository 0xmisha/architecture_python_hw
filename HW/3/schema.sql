-- ============================================================
-- Hotel Booking System — Schema (Variant 13)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ------------------------------------------------------------
-- Users
-- ------------------------------------------------------------
CREATE TABLE users (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    login         VARCHAR(50)  NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_users_login UNIQUE (login),
    CONSTRAINT uq_users_email UNIQUE (email)
);

-- ------------------------------------------------------------
-- Hotels
-- ------------------------------------------------------------
CREATE TABLE hotels (
    id              UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255)   NOT NULL,
    city            VARCHAR(100)   NOT NULL,
    address         VARCHAR(500)   NOT NULL,
    stars           SMALLINT       NOT NULL,
    rooms_total     INTEGER        NOT NULL,
    price_per_night NUMERIC(12, 2) NOT NULL,
    created_at      TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_hotels_stars        CHECK (stars BETWEEN 1 AND 5),
    CONSTRAINT chk_hotels_rooms_total  CHECK (rooms_total > 0),
    CONSTRAINT chk_hotels_price        CHECK (price_per_night > 0)
);

-- ------------------------------------------------------------
-- Bookings
-- ------------------------------------------------------------
CREATE TABLE bookings (
    id          UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID           NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    hotel_id    UUID           NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    check_in    DATE           NOT NULL,
    check_out   DATE           NOT NULL,
    total_price NUMERIC(12, 2) NOT NULL,
    status      VARCHAR(20)    NOT NULL DEFAULT 'confirmed',
    created_at  TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_booking_dates  CHECK (check_out > check_in),
    CONSTRAINT chk_booking_price  CHECK (total_price >= 0),
    CONSTRAINT chk_booking_status CHECK (status IN ('confirmed', 'cancelled'))
);

-- ============================================================
-- Indexes
-- ============================================================

-- Exact login lookup (used in /auth/login and /users/search?login=)
CREATE INDEX idx_users_login ON users(login);

-- Name/surname substring search (ILIKE, used in /users/search?name=)
CREATE INDEX idx_users_first_name ON users USING gin (first_name gin_trgm_ops);
CREATE INDEX idx_users_last_name  ON users USING gin (last_name  gin_trgm_ops);

-- City substring search (ILIKE, used in /hotels/search?city=)
CREATE INDEX idx_hotels_city ON hotels USING gin (city gin_trgm_ops);

-- Stars filter (used in analytical / range queries)
CREATE INDEX idx_hotels_stars ON hotels(stars);

-- FK index: get all bookings for a user (used in /bookings/my)
CREATE INDEX idx_bookings_user_id ON bookings(user_id);

-- FK index: analytics per hotel
CREATE INDEX idx_bookings_hotel_id ON bookings(hotel_id);

-- Composite: active bookings for a user (most frequent query pattern)
CREATE INDEX idx_bookings_user_status ON bookings(user_id, status);

-- Date range: availability checks, reporting
CREATE INDEX idx_bookings_dates ON bookings(hotel_id, check_in, check_out);

