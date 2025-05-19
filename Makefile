# Makefile for PantryPal – AI Recipe Generator

# Variables
VENV      := .venv
PYTHON    := $(VENV)/bin/python
PIP       := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit
DC        := docker-compose

# Default target
.PHONY: help
help:
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  venv           Create Python virtual environment"
	@echo "  install        Install dependencies into venv"
	@echo "  update         Upgrade dependencies to latest"
	@echo "  lint           Check code style with Black & isort"
	@echo "  format         Apply Black & isort to format code"
	@echo "  run            Launch Streamlit app"
	@echo "  analysis       Run analysis scripts"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-up      Run app via Docker Compose"
	@echo "  clean          Remove venv & cache"
	@echo ""

# Create virtual environment
.PHONY: venv
venv:
	python3 -m venv $(VENV)
	@echo "Virtual environment created at $(VENV). Activate with 'source $(VENV)/bin/activate'."

# Install dependencies
.PHONY: install
install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Upgrade dependencies
.PHONY: update
update: venv
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt

# Linting checks
.PHONY: lint
lint:
	$(VENV)/bin/black --check .
	$(VENV)/bin/isort --check .

# Auto-format code
.PHONY: format
format:
	$(VENV)/bin/black .
	$(VENV)/bin/isort .

# Run Streamlit app
.PHONY: run
run:
	$(STREAMLIT) run app.py

# Run all analysis scripts
.PHONY: analysis
analysis:
	$(PYTHON) analysis/ingredient_frequency.py
	$(PYTHON) analysis/nutrition_summary.py
	$(PYTHON) analysis/trends_over_time.py

# Docker: build & up
.PHONY: docker-build
docker-build:
	$(DC) build

.PHONY: docker-up
docker-up:
	$(DC) up --build

# Clean up virtualenv and caches
.PHONY: clean
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleaned virtualenv and Python cache."

