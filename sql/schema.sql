CREATE TABLE IF NOT EXISTS temperature_readings (
    reading_id TEXT,
    room_id TEXT,
    noted_date TIMESTAMP,
    temperature DOUBLE PRECISION,
    location TEXT
);
