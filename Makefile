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
	pytest test
