CREATE TABLE IF NOT EXISTS app_logs (
    timestamp DateTime,
    level String,
    logger String,
    module String,
    function String,
    line UInt32,
    message String,
    exception String DEFAULT '',
    user_id String DEFAULT '',
    request_id String DEFAULT '',
    duration_ms UInt32 DEFAULT 0,
    
    -- Партиционирование по дням (для быстрого удаления старых логов)
    event_date Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (timestamp, level, logger)
TTL event_date + INTERVAL 30 DAY  -- логи хранятся 30 дней
SETTINGS index_granularity = 8192