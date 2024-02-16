.PHONY: lint check

lint:
	python -m ruff .

check:
	python -m pyright .