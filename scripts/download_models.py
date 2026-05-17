"""Create model directories and prewarm placeholders."""

from src.models.downloader import download_required_models


def main() -> None:
    """Entrypoint."""
    download_required_models()


if __name__ == "__main__":
    main()
