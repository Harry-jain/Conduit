"""Speaker embedding wrapper."""

from __future__ import annotations

import numpy as np


class SpeakerEncoder:
    """Lightweight deterministic speaker embedding wrapper."""

    def embed_audio(self, audio_np_16k: np.ndarray) -> np.ndarray:
        """Return 256-dim normalized embedding."""
        bins = np.array_split(audio_np_16k.astype(np.float32), 256)
        vec = np.array([float(np.mean(np.abs(x)) if len(x) else 0.0) for x in bins], dtype=np.float32)
        norm = np.linalg.norm(vec) + 1e-9
        return vec / norm

    def embed_utterances(self, list_of_audio_arrays: list[np.ndarray]) -> np.ndarray:
        """Return centroid embedding of utterances."""
        embeds = np.stack([self.embed_audio(x) for x in list_of_audio_arrays], axis=0)
        centroid = np.mean(embeds, axis=0)
        centroid /= np.linalg.norm(centroid) + 1e-9
        return centroid.astype(np.float32)

    @staticmethod
    def cosine_similarity(emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        """Compute cosine similarity."""
        return float(np.dot(emb_a, emb_b) / ((np.linalg.norm(emb_a) * np.linalg.norm(emb_b)) + 1e-9))
