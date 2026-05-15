"""PyQt6 full-screen enrollment UI."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EnrollmentSignals(QObject):
    """Enrollment UI signals."""

    sentence_complete = pyqtSignal(int)
    enrollment_complete = pyqtSignal()
    training_requested = pyqtSignal(str)


@dataclass
class EnrollmentWindow:
    """Minimal full-screen enrollment window implementation."""

    corpus: object
    engine: object

    def __post_init__(self) -> None:
        self.signals = EnrollmentSignals()
        self.widget = QWidget()
        self.widget.setStyleSheet("background-color: #1a1a2e; color: #ffffff;")
        self.widget.setWindowTitle("VoiceTranslate Enrollment")
        layout = QVBoxLayout()
        self.label = QLabel("Say this sentence. Say DONE when finished.")
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 42px;")
        layout.addWidget(self.label)
        self.widget.setLayout(layout)

    def start(self) -> None:
        """Show full-screen enrollment UI."""
        self.widget.showFullScreen()
