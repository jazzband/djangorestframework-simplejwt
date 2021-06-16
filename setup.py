#!/usr/bin/env python
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
        'pytest-watch',
        'wheel',
        'twine',
        'ipython',
    ],
    'python-jose': [
        'python-jose==3.0.0',
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
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    url='https://github.com/jazzband/djangorestframework-simplejwt',
    license='MIT',
    description='A minimal JSON Web Token authentication plugin for Django REST Framework',
    long_description=open('README.rst', 'r', encoding='utf-8').read(),
    author='David Sanders',
    author_email='davesque@gmail.com',
    install_requires=[
        'django',
        'djangorestframework',
        'pyjwt>=2,<3',
    ],
    python_requires='>=3.7',
    extras_require=extras_require,
    packages=find_packages(exclude=['tests', 'tests.*', 'licenses', 'requirements']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
