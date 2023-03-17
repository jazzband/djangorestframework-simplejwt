
To do development work for Ninja JWT, make your own fork on Github,
clone it locally, make and activate a virtualenv for it, then from
within the project directory:

After that, install flit

```shell
$(venv) pip install flit
```

Install development libraries and pre-commit hooks for code linting and styles

```shell
$(venv) make install
```

To run the tests:

```shell
$(venv) make test
```

To run the tests with coverage:

```shell
$(venv) make test-cov
```
