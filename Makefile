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

ifeq ($(OS),Windows_NT)
	CREATE_ENV := virtualenv env
    RM := "rm" -rf
    FIND := "C:\Program Files\Git\usr\bin\find.exe"
	ENV := env\Scripts\\
else
	CREATE_ENV := virtualenv --python $(PYTHON3) env
    ENV := env/bin/
	RM := rm -rf
	FIND := find
endif

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
	$(RM) env
	$(RM) build
	$(RM) dist
	$(RM) .eggs
	$(FIND) . -name '*.egg-info' -exec rm -fr {} +
	$(FIND) . -name '*.egg' -exec rm -fr {} +

clean-pyc:
	$(FIND) . -name '*.pyc' -exec rm -f {} +
	$(FIND) . -name '*.pyo' -exec rm -f {} +
	$(FIND) . -name '*~' -exec rm -f {} +
	$(FIND) . -name '__pycache__' -exec rm -fr {} +

clean-test:
	$(RM) .coverage
	$(RM) htmlcov

install: clean
	$(CREATE_ENV)
	$(ENV)pip install --upgrade -r requirements.txt

install-codeship: install
	$(ENV)pip install coverage

install-dev: clean
	$(CREATE_ENV)
	$(ENV)pip install --upgrade -r requirements_dev.txt

lint:
	$(ENV)flake8 --max-complexity=10 main.py platforms tests/test_*.py

test:
	$(ENV)python tests/test_*.py

coverage:
	$(ENV)coverage run --branch --source main.py,platforms tests/test_*.py
	$(ENV)coverage report -m
	$(ENV)coverage html
	$(BROWSER) htmlcov/index.html

coverage-codeship:
	
	$(ENV)coverage run --branch --source main.py,platforms tests/test_*.py
	$(ENV)coverage report -m --fail-under 100
