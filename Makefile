VENV ?= .venv
PYTHON ?= $(VENV)/bin/python

.PHONY: install run test lint check clean

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) -m streamlit run app.py

test:
	$(PYTHON) -m pytest

check:
	$(PYTHON) -c "from mybestsim.config import DATA_DIR; from mybestsim.etl import clean_data, load_raw; df = clean_data(load_raw(DATA_DIR)); print(f'{len(df)} offres valides')"

lint:
	$(PYTHON) -m ruff check .

clean:
	rm -rf *.egg-info .pytest_cache .ruff_cache
