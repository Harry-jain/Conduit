"""Global constants for supported languages and audio defaults."""

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "ja": "Japanese",
    "de": "German",
    "it": "Italian",
    "fr": "French",
    "ru": "Russian",
    "hi": "Hindi",
}

NLLB_LANG_CODES: dict[str, str] = {
    "en": "eng_Latn",
    "es": "spa_Latn",
    "ja": "jpn_Jpan",
    "de": "deu_Latn",
    "it": "ita_Latn",
    "fr": "fra_Latn",
    "ru": "rus_Cyrl",
    "hi": "hin_Deva",
}

SAMPLE_RATE = 16000
CHUNK_SIZE_MS = 32
LOOPBACK_SAMPLE_RATE = 48000
TTS_SAMPLE_RATE = 22050
