.PHONY: all format lint test clean

all: format lint test

format:
	black src tests

lint:
	ruff check .

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .venv