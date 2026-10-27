VENV ?= .venv
PYTHON ?= $(VENV)/bin/python

.PHONY: install run test lint check article clean

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) -m streamlit run app.py

test:
	$(PYTHON) -m pytest

check:
	$(PYTHON) -m mybestsim.check

article:
	uv run --no-project --with "markdown>=3.6" python article/build.py

lint:
	$(PYTHON) -m ruff check .

clean:
	rm -rf *.egg-info .pytest_cache .ruff_cache
