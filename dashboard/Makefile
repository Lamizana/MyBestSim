VENV ?= .venv
PYTHON ?= $(VENV)/bin/python

.PHONY: install data test lint clean

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -e ".[dev]"

data:
	$(PYTHON) -m mybestsim

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

clean:
	rm -rf data/processed site *.egg-info .pytest_cache .ruff_cache
