.PHONY: default
default: black lint test

.PHONY: black
black:
	black test src client

.PHONY: lint
lint:
	ruff check src/battleship/*.py client/*.py

.PHONY: test
test:
	pytest test/test_api.py test/test_utils.py

