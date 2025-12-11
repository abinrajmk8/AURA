-- AURA Database Schema

-- Table: alerts
-- Stores all security events triggered by the IDS
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    src_ip TEXT NOT NULL,
    dst_ip TEXT,
    alert_type TEXT NOT NULL, -- 'OSINT', 'ML', 'HEURISTIC', 'JA3'
    severity TEXT DEFAULT 'HIGH',
    description TEXT,
    payload TEXT, -- Capture snippet of payload for review
    action_taken TEXT -- 'BLOCKED', 'LOGGED'
);

-- Table: flows
-- Stores raw flow features for future ML retraining
-- Only stores flows marked for review or confirmed attacks
CREATE TABLE IF NOT EXISTS flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    src_ip TEXT,
    dst_ip TEXT,
    dst_port INTEGER,
    protocol INTEGER,
    features TEXT, -- JSON string of the extracted features
    label TEXT DEFAULT 'UNKNOWN' -- 'MALICIOUS', 'BENIGN' (for retraining)
);

-- Table: osint_rules
-- Stores the active intelligence feed
CREATE TABLE IF NOT EXISTS osint_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_value TEXT UNIQUE NOT NULL, -- IP, Regex, Hash
    rule_type TEXT NOT NULL, -- 'ipv4', 'micro_rule', 'ja3_hash'
    source TEXT,
    confidence REAL,
    last_seen DATETIME,
    tags TEXT -- JSON list of tags
);
