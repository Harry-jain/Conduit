.PHONY: run enroll train-local train-colab test test-unit test-int \
        lint format typecheck benchmark download clean

run:
	python -m src.main

enroll:
	python -m src.main enroll

train-local:
	python -m src.main train --mode local

train-colab:
	python -m src.main train --mode colab

test:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing \
	       -m "not integration" -v

test-unit:
	pytest tests/unit/ -v --tb=short

test-int:
	pytest tests/integration/ -v --tb=short -m integration

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/ --ignore-missing-imports

benchmark:
	python scripts/benchmark_latency.py

download:
	python scripts/download_models.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
