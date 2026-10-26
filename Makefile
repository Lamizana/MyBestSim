VENV ?= .venv
PYTHON ?= $(VENV)/bin/python

.PHONY: install run test lint clean

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) -m streamlit run app.py

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

clean:
	rm -rf *.egg-info .pytest_cache .ruff_cache
