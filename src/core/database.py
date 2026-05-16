"""SQLite database initialization and helpers."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

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
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def upsert_user_config(conn: sqlite3.Connection, key: str, value: str) -> None:
    """Insert or update a user configuration key."""
    conn.execute(
        """
        INSERT INTO user_config (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
        """,
        (key, value),
    )
    conn.commit()


def get_user_config(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    """Read a user configuration key with optional default."""
    row = conn.execute("SELECT value FROM user_config WHERE key = ?", (key,)).fetchone()
    if row is None:
        return default
    return str(row["value"])


def create_enrollment_session(conn: sqlite3.Connection, total_sentences: int = 60) -> int:
    """Create and return a new enrollment session id."""
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO enrollment_sessions (started_at, total_sentences, status)
        VALUES (?, ?, 'in_progress')
        """,
        (datetime.utcnow().isoformat(), total_sentences),
    )
    conn.commit()
    return int(cur.lastrowid or 0)


def mark_enrollment_complete(conn: sqlite3.Connection, session_id: int) -> None:
    """Mark enrollment session as complete."""
    conn.execute(
        """
        UPDATE enrollment_sessions
        SET status = 'complete', completed_at = ?
        WHERE id = ?
        """,
        (datetime.utcnow().isoformat(), session_id),
    )
    conn.commit()


def insert_recording_segment(
    conn: sqlite3.Connection,
    session_id: int,
    sentence_index: int,
    sentence_text: str,
    audio_path: str,
    mel_path: str,
    duration_s: float,
    snr_db: float,
    accepted: bool,
    rejection_reason: str | None,
) -> None:
    """Persist one enrollment recording segment row."""
    conn.execute(
        """
        INSERT INTO recording_segments (
            session_id, sentence_index, sentence_text, audio_path, mel_path,
            duration_s, snr_db, accepted, rejection_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            sentence_index,
            sentence_text,
            audio_path,
            mel_path,
            duration_s,
            snr_db,
            int(accepted),
            rejection_reason,
        ),
    )
    conn.execute(
        """
        UPDATE enrollment_sessions
        SET sentences_done = (
            SELECT COUNT(*) FROM recording_segments
            WHERE session_id = ? AND accepted = 1
        )
        WHERE id = ?
        """,
        (session_id, session_id),
    )
    conn.commit()


def create_training_run(conn: sqlite3.Connection, mode: str) -> int:
    """Create a new training run and return its id."""
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO training_runs (mode, started_at, status)
        VALUES (?, ?, 'running')
        """,
        (mode, datetime.utcnow().isoformat()),
    )
    conn.commit()
    return int(cur.lastrowid or 0)


def complete_training_run(
    conn: sqlite3.Connection,
    run_id: int,
    epochs_done: int,
    best_mcd: float | None,
    best_secs: float | None,
    checkpoint_path: str | None,
    status: str = "complete",
) -> None:
    """Mark training run completion metadata."""
    conn.execute(
        """
        UPDATE training_runs
        SET completed_at = ?, epochs_done = ?, best_mcd = ?, best_secs = ?,
            checkpoint_path = ?, status = ?
        WHERE id = ?
        """,
        (
            datetime.utcnow().isoformat(),
            epochs_done,
            best_mcd,
            best_secs,
            checkpoint_path,
            status,
            run_id,
        ),
    )
    conn.commit()


def insert_pipeline_metric(conn: sqlite3.Connection, payload: dict[str, Any]) -> None:
    """Insert one pipeline metrics record."""
    conn.execute(
        """
        INSERT INTO pipeline_metrics (
            pipeline, e2e_latency_ms, asr_latency_ms, mt_latency_ms, tts_latency_ms,
            gpu_temp_c, vram_used_mb
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("pipeline", "unknown"),
            float(payload.get("e2e_latency_ms", 0.0)),
            float(payload.get("asr_latency_ms", 0.0)),
            float(payload.get("mt_latency_ms", 0.0)),
            float(payload.get("tts_latency_ms", 0.0)),
            int(payload.get("gpu_temp_c", 0)),
            int(payload.get("vram_used_mb", 0)),
        ),
    )
    conn.commit()
