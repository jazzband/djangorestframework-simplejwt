.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Removing cached python compiled files
	find . -name \*pyc  | xargs  rm -fv
	find . -name \*pyo | xargs  rm -fv
	find . -name \*~  | xargs  rm -fv
	find . -name __pycache__  | xargs  rm -rfv

install: ## Install dependencies
	make clean
	flit install --deps develop --symlink
	pre-commit install -f

lint: ## Run code linters
	make clean
	black --check ninja_jwt tests
	ruff check ninja_jwt tests
# 	mypy  ninja_jwt

fmt format: ## Run code formatters
	make clean
	black ninja_jwt tests
	ruff check --fix ninja_jwt tests

test: ## Run tests
	make clean
	pytest .

test-cov: ## Run tests with coverage
	make clean
	pytest --cov=ninja_jwt --cov-report term-missing tests

doc-deploy: ## Run Deploy Documentation
	make clean
	mkdocs gh-deploy --force

doc-serve: ## Run Deploy Documentation
	make clean
	mkdocs serve
