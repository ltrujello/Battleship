.PHONY: default
default: black lint test

.PHONY: black
black:
	black test src

.PHONY: lint
lint:
	ruff check src/battleship/*.py        

.PHONY: test
test:
	pytest test/test_api test/test_utils.py

