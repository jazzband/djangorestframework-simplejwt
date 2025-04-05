.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Removing cached python compiled files
	find . -name \*pyc  | xargs  rm -fv
	find . -name \*pyo | xargs  rm -fv
	find . -name \*~  | xargs  rm -fv
	find . -name __pycache__  | xargs  rm -rfv
	find . -name .ruff_cache  | xargs  rm -rfv

install:clean ## Install dependencies
	pip install -r requirements.txt
	flit install --symlink

install-full:install ## Install dependencies
	pre-commit install -f

lint:fmt ## Run code linters
	ruff check ninja_jwt tests
# 	mypy  ninja_jwt

fmt format:clean ## Run code formatters
	ruff format ninja_jwt tests
	ruff check --fix ninja_jwt tests

test:clean ## Run tests
	pytest .

test-cov:clean ## Run tests with coverage
	pytest --cov=ninja_jwt --cov-report term-missing tests

doc-deploy:clean ## Run Deploy Documentation
	mkdocs gh-deploy --force

doc-serve:clean ## Run Deploy Documentation
	mkdocs serve
