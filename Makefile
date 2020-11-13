CURRENT_SIGN_SETTING := $(shell git config commit.gpgSign)

.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "isortfix - fixes the imports order"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

isortfix:
	isort --recursive --skip migrations docs

lint:
	tox -e lint

lint-roll:
	isort rest_framework_simplejwt tests
	$(MAKE) lint

test:
	pytest tests

test-all:
	tox

build-docs:
	sphinx-apidoc -o docs/ . \
		setup.py \
		*confest* \
		tests/* \
		rest_framework_simplejwt/token_blacklist/* \
		rest_framework_simplejwt/backends.py \
		rest_framework_simplejwt/compat.py \
		rest_framework_simplejwt/exceptions.py \
		rest_framework_simplejwt/settings.py \
		rest_framework_simplejwt/state.py
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(MAKE) -C docs doctest

docs: build-docs
	open docs/_build/html/index.html

linux-docs: build-docs
	xdg-open docs/_build/html/index.html

release: clean
	bumpversion $(bump)
	git push upstream && git push upstream --tags
	python setup.py sdist bdist_wheel
	twine upload dist/*

dist: clean
	python setup.py sdist bdist_wheel
	ls -l dist
