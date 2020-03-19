.. _development_and_contributing:

Development and Contributing
============================

To do development work for Simple JWT, make your own fork on Github, clone it
locally, make and activate a virtualenv for it, then from within the project
directory:

.. code-block:: bash

  pip install --upgrade pip setuptools
  pip install -e .[dev]

To run the tests:

.. code-block:: bash

  pytest

To run the tests in all supported environments with tox, first `install pyenv
<https://github.com/pyenv/pyenv#installation>`__.  Next, install the relevant
Python minor versions and create a ``.python-version`` file in the project
directory:

.. code-block:: bash

  pyenv install 3.8.x
  pyenv install 3.7.x
  pyenv install 3.6.x
  cat > .python-version <<EOF
  3.8.x
  3.7.x
  3.6.x
  EOF

Above, the ``x`` in each case should be replaced with the latest corresponding
patch version.  The ``.python-version`` file will tell pyenv and tox that
you're testing against multiple versions of Python.  Next, run tox:

.. code-block:: bash

  tox
