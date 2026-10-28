VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
PYTHON_VERSION ?= 3.12

.PHONY: install run test lint check article clean

install:
	uv venv $(VENV) --python $(PYTHON_VERSION) --seed --clear
	$(PYTHON) -m pip install --upgrade pip
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
