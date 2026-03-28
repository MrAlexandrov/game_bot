.PHONY: install
install:
	poetry install

.PHONY: install-dev
install-dev:
	poetry install --with dev

.PHONY: run
run:
	poetry run python -m src.main

.PHONY: lint
lint:
	poetry run flake8 src/

.PHONY: format
format:
	poetry run black src/

.PHONY: clean
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
