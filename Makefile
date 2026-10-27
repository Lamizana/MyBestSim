VENV ?= .venv
PYTHON ?= $(VENV)/bin/python

.PHONY: install reqs reqs-check run test lint check clean

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) -m streamlit run app.py

reqs:
	uv pip compile pyproject.toml --python-version 3.12 --no-header -o requirements.txt

reqs-check:
	uv pip compile pyproject.toml --python-version 3.12 --no-header | diff -u requirements.txt -

test:
	$(PYTHON) -m pytest

check:
	$(PYTHON) -m mybestsim.check

lint:
	$(PYTHON) -m ruff check .

clean:
	rm -rf *.egg-info .pytest_cache .ruff_cache
