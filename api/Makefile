.PHONY: install test lint format clean

install:
	pip install -e ".[dev]"

test:
	pytest src/realtime_chat/tests/ -v --cov=realtime_chat

lint:
	mypy src/realtime_chat
	flake8 src/realtime_chat
	black --check src/realtime_chat
	isort --check src/realtime_chat

format:
	black src/realtime_chat
	isort src/realtime_chat

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +