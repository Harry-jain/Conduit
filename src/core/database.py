"""SQLite database initialization and helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS user_config (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enrollment_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at      DATETIME NOT NULL,
    completed_at    DATETIME,
    sentences_done  INTEGER DEFAULT 0,
    total_sentences INTEGER DEFAULT 60,
    status          TEXT DEFAULT 'in_progress'
);

CREATE TABLE IF NOT EXISTS recording_segments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER REFERENCES enrollment_sessions(id),
    sentence_index   INTEGER NOT NULL,
    sentence_text    TEXT NOT NULL,
    audio_path       TEXT NOT NULL,
    mel_path         TEXT NOT NULL,
    duration_s       REAL NOT NULL,
    snr_db           REAL NOT NULL,
    accepted         BOOLEAN NOT NULL,
    rejection_reason TEXT,
    recorded_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS training_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    mode            TEXT NOT NULL,
    started_at      DATETIME NOT NULL,
    completed_at    DATETIME,
    epochs_done     INTEGER DEFAULT 0,
    best_mcd        REAL,
    best_secs       REAL,
    checkpoint_path TEXT,
    status          TEXT DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS pipeline_metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline        TEXT NOT NULL,
    e2e_latency_ms  REAL NOT NULL,
    asr_latency_ms  REAL NOT NULL,
    mt_latency_ms   REAL NOT NULL,
    tts_latency_ms  REAL NOT NULL,
    gpu_temp_c      INTEGER,
    vram_used_mb    INTEGER,
    recorded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection(db_path: str = "voicetranslate.db") -> sqlite3.Connection:
    """Open SQLite connection and initialize schema."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn
