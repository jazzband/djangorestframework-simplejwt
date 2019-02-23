#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    'test': [
        'cryptography',
        'pytest-cov',
        'pytest-django',
        'pytest-xdist',
        'pytest',
        'tox',
    ],
    'lint': [
        'flake8',
        'pep8',
        'isort',
    ],
    'doc': [
        'Sphinx>=1.6.5,<2',
        'sphinx_rtd_theme>=0.1.9',
    ],
    'dev': [
        'bumpversion>=0.5.3,<1',
        'pytest-watch',
        'wheel',
        'twine',
        'ipython',
    ],
    'python-jose': [
        'python-jose==1.3.2',
    ],
}

extras_require['dev'] = (
    extras_require['dev'] +  # noqa: W504
    extras_require['test'] +  # noqa: W504
    extras_require['lint'] +  # noqa: W504
    extras_require['doc'] +  # noqa: W504
    extras_require['python-jose']
)


setup(
    name='djangorestframework_simplejwt',
    version='3.3.0',
    url='https://github.com/davesque/django-rest-framework-simplejwt',
    license='MIT',
    description='A minimal JSON Web Token authentication plugin for Django REST Framework',
    long_description=open('README.rst', 'r', encoding='utf-8').read(),
    author='David Sanders',
    author_email='davesque@gmail.com',
    install_requires=[
        'django',
        'djangorestframework',
        'pyjwt',
    ],
    extras_require=extras_require,
    packages=find_packages(exclude=['tests', 'tests.*', 'licenses', 'requirements']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
