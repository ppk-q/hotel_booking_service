-- SQL-скрипт для ручного создания таблиц в PostgreSQL
CREATE TABLE IF NOT EXISTS rooms (
    id BIGSERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    price_per_night NUMERIC(10, 2) NOT NULL CHECK (price_per_night >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bookings (
    id BIGSERIAL PRIMARY KEY,
    room_id BIGINT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    date_start DATE NOT NULL,
    date_end DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (date_end >= date_start)
);

CREATE INDEX IF NOT EXISTS idx_bookings_room_start ON bookings (room_id, date_start);
CREATE INDEX IF NOT EXISTS idx_bookings_room_end ON bookings (room_id, date_end);
