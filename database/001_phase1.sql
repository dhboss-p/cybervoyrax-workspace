-- Phase 1 database initialization.
-- Phase 2 will replace this with the full CYBERVOYRAX schema and deterministic seed engine.

CREATE TABLE IF NOT EXISTS app_meta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meta_key VARCHAR(100) NOT NULL UNIQUE,
    meta_value VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO app_meta (meta_key, meta_value)
VALUES ('phase', '1')
ON DUPLICATE KEY UPDATE meta_value = VALUES(meta_value);
