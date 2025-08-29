#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages, setup

extras_require = {
    "test": [
        "cryptography",
        "freezegun",
        "pytest-cov",
        "pytest-django",
        "pytest-xdist",
        "pytest",
        "tox",
    ],
    "lint": [
        "ruff",
        "yesqa",
        "pyupgrade",
        "pre-commit",
    ],
    "doc": [
        "Sphinx",
        "sphinx_rtd_theme>=0.1.9",
    ],
    "dev": [
        "pytest-watch",
        "wheel",
        "twine",
        "ipython",
    ],
    "python-jose": [
        "python-jose==3.3.0",
    ],
    "crypto": [
        "cryptography>=3.3.1",
    ],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["test"]
    + extras_require["lint"]
    + extras_require["doc"]
    + extras_require["python-jose"]
)


setup(
    name="djangorestframework_simplejwt",
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    url="https://github.com/jazzband/djangorestframework-simplejwt",
    license="MIT",
    description="A minimal JSON Web Token authentication plugin for Django REST Framework",
    long_description=Path("README.rst").read_text(encoding="utf-8"),
    author="David Sanders",
    author_email="davesque@gmail.com",
    install_requires=[
        "django>=4.2",
        "djangorestframework>=3.14",
        "pyjwt>=1.7.1",
    ],
    python_requires=">=3.9",
    extras_require=extras_require,
    packages=find_packages(exclude=["tests", "tests.*", "licenses", "requirements"]),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
