.PHONY: clean-pyc clean-build clean
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"
PYTHON3 ?= /usr/local/bin/python3

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr .venv
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr htmlcov/

install: clean
	virtualenv --python $(PYTHON3) .venv
	. .venv/bin/activate && \
	pip install --upgrade -r requirements.txt

install-codeship: install
	. .venv/bin/activate && \
	pip install coverage

install-dev: clean
	virtualenv --python $(PYTHON3) .venv
	. .venv/bin/activate && \
	pip install --upgrade -r requirements_dev.txt

lint:
	. .venv/bin/activate && \
	flake8 --max-complexity=10 main.py platforms tests/test_*.py

test:
	. .venv/bin/activate && \
	python tests/test_*.py

coverage:
	. .venv/bin/activate && \
	coverage run --branch --source main.py,platforms tests/test_*.py && \
	coverage report -m && \
	coverage html && \
	$(BROWSER) htmlcov/index.html

coverage-codeship:
	. .venv/bin/activate && \
	coverage run --branch --source main.py,platforms tests/test_*.py && \
	coverage report -m --fail-under 100
