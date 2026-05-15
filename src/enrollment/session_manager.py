"""Enrollment session state manager."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.database import get_connection


@dataclass
class SessionState:
    session_id: int
    sentences_done: int
    total_sentences: int
    status: str


class EnrollmentSessionManager:
    """Database-backed enrollment session tracker."""

    def __init__(self, db_path: str = "voicetranslate.db") -> None:
        self.conn = get_connection(db_path)

    def start(self) -> SessionState:
        """Create a new enrollment session."""
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO enrollment_sessions(started_at, total_sentences, status) VALUES (?, ?, ?)",
            (datetime.utcnow().isoformat(), 60, "in_progress"),
        )
        self.conn.commit()
        session_id = int(cur.lastrowid)
        return SessionState(session_id=session_id, sentences_done=0, total_sentences=60, status="in_progress")

    def increment(self, session_id: int) -> None:
        """Increment completed sentence count."""
        self.conn.execute(
            "UPDATE enrollment_sessions SET sentences_done = sentences_done + 1 WHERE id = ?",
            (session_id,),
        )
        self.conn.commit()
