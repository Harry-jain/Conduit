"""Custom exception hierarchy for VoiceTranslate."""


class VoiceTranslateError(Exception):
    """Base exception for the application."""


class ConfigValidationError(VoiceTranslateError):
    """Raised when configuration is invalid."""


class AudioDeviceError(VoiceTranslateError):
    """Raised when an audio device cannot be accessed."""


class ModelLoadError(VoiceTranslateError):
    """Raised when a model fails to load."""


class TrainingError(VoiceTranslateError):
    """Raised when a training operation fails."""


class VRAMError(VoiceTranslateError):
    """Raised when available VRAM is insufficient."""
