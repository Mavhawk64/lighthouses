# Makefile for USCG lighthouse scraper
# Usage examples:
#   make help
#   make venv install
#   make playwright
#   make run URL="https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Lighthouses/"
#   make reqs            # pipreqs -> requirements.txt
#   make reqs-txt        # pipreqs -> requests.txt
#   make lock            # pip freeze -> requirements-lock.txt
#   make clean | make nuke

SHELL := /usr/bin/env bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ====== Config ======
# Choose your Python; use the venv you prefer. Default: .venv in repo root.
PY ?= python3
PIP ?= pip
VENV_DIR ?= .venv
ACTIVATE := source $(VENV_DIR)/bin/activate

# Path to your scraper module
SCRAPER := src/scraper/coast_guard_scraper.py

# ====== Meta ======
.PHONY: help venv install playwright run reqs reqs-txt lock clean nuke upgrade check pipreqs ppw-deps pw-install

help:
	@echo "Targets:"
	@echo "  venv        - Create a virtualenv in $(VENV_DIR)"
	@echo "  install     - Install runtime deps (requests, bs4, lxml, playwright)"
	@echo "  playwright  - Download browser engines (Chromium) for Playwright"
	@echo "  run         - Run scraper (set URL=...)"
	@echo "  reqs        - Generate requirements.txt via pipreqs"
	@echo "  reqs-txt    - Generate requests.txt via pipreqs (your requested name)"
	@echo "  lock        - Freeze exact versions to requirements-lock.txt"
	@echo "  upgrade     - Upgrade pip, setuptools, wheel"
	@echo "  clean       - Remove __pycache__ and build artifacts"
	@echo "  nuke        - Clean + remove virtualenv"

# ====== Environment / deps ======
venv:
	@ if [ ! -d "$(VENV_DIR)" ]; then \
		$(PY) -m venv $(VENV_DIR); \
		echo "Created venv at $(VENV_DIR)"; \
	else \
		echo "Venv exists at $(VENV_DIR)"; \
	fi
	@ $(ACTIVATE); \
	$(PY) -V; \
	python -c "import sys; print('venv OK:', sys.prefix)"

upgrade: venv
	@ $(ACTIVATE); \
	$(PIP) install --upgrade pip setuptools wheel

install: venv upgrade
	@ $(ACTIVATE); \
	$(PIP) install requests beautifulsoup4 lxml playwright

playwright: venv
	@ $(ACTIVATE); \
	$(PY) -m playwright install chromium

check:
	@ test -f "$(SCRAPER)" || (echo "Missing $(SCRAPER)"; exit 1)

pipreqs: venv
	@ $(ACTIVATE); \
	$(PIP) install pipreqs

.PHONY: pw-deps pw-install

# System libraries required by Playwright browsers (for WSL/Ubuntu)
pw-deps:
	@ sudo apt-get update
	@ sudo apt-get install -y \
		libglib2.0-0 libnspr4 libnss3 \
		libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 \
		libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
		libgbm1 libxkbcommon0 libasound2
	@ echo "Playwright system deps installed."

# Download Chromium engine for Playwright into the current venv
pw-install: playwright
	@ $(ACTIVATE); \
	$(PY) -m playwright install chromium


# ====== Run ======
# Example:
#   make run URL="https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Lighthouses/"
run: check
	@ if [ -z "$$URL" ]; then \
		echo "Please provide URL, e.g. make run URL=https://example.com"; \
		exit 1; \
	fi
	@ $(ACTIVATE); \
	$(PY) "$(SCRAPER)"

# ====== Requirements tracking ======
# Generate based on imports actually used in your codebase
reqs: pipreqs
	@ $(ACTIVATE); \
	pipreqs . --force --encoding=utf-8 --savepath=requirements.txt
	@ echo "Wrote requirements.txt from imports detected by pipreqs."

# Same, but to 'requests.txt' since you asked for that specific filename.
reqs-txt: pipreqs
	@ $(ACTIVATE); \
	pipreqs . --force --encoding=utf-8 --savepath=requests.txt
	@ echo "Wrote requests.txt from imports detected by pipreqs."

# Lock exact versions of the current venv (useful for reproducibility)
lock:
	@ $(ACTIVATE); \
	$(PIP) freeze | sed '/^-e /d' > requirements-lock.txt
	@ echo "Wrote requirements-lock.txt"

# ====== Housekeeping ======
clean:
	@ find . -type d -name "__pycache__" -prune -exec rm -rf {} +; \
	find . -type f -name "*.pyc" -delete; \
	find . -type f -name "*.pyo" -delete; \
	echo "Cleaned pyc/pyo and __pycache__."

nuke: clean
	@ rm -rf "$(VENV_DIR)"; \
	echo "Removed venv $(VENV_DIR)."
