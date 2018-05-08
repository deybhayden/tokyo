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

ifeq ($(OS),Windows_NT)
	RM := "rm" -rf
	FIND := "C:\Program Files\Git\usr\bin\find.exe"
else
	RM := rm -rf
	FIND := find
endif

.PHONY: clean-pyc clean-build clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with pylint"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "install - install tokyo's dependencies to the active Python's site-packages"
	@echo "install-dev - install tokyo's dependencies to the active Python's site-packages plus debug tools for local development"

clean: clean-build clean-pyc clean-test

clean-build:
	pyenv uninstall -f tokyo
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
	pyenv virtualenv 3.6.5 tokyo
	pip install --upgrade -r requirements.txt
	python -m nltk.downloader brown

install-dev: clean
	pyenv virtualenv 3.6.5 tokyo
	pip install --upgrade -r requirements_dev.txt
	python -m nltk.downloader brown

lint:
	pylint main.py platforms tests/test_tokyo.py

test:
	python tests/test_tokyo.py

coverage:
	coverage run --branch --source main.py,platforms tests/test_tokyo.py
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html
