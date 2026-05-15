"""Create model directories and prewarm placeholders."""

from src.models.downloader import ensure_model_dirs


def main() -> None:
    """Entrypoint."""
    ensure_model_dirs()


if __name__ == "__main__":
    main()
