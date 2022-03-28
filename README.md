# Ninja JWT
![Test](https://github.com/eadwinCode/django-ninja-jwt/workflows/Test/badge.svg)
[![PyPI version](https://badge.fury.io/py/django-ninja-jwt.svg)](https://badge.fury.io/py/django-ninja-jwt)
[![PyPI version](https://img.shields.io/pypi/v/django-ninja-jwt.svg)](https://pypi.python.org/pypi/django-ninja-jwt)
[![PyPI version](https://img.shields.io/pypi/pyversions/django-ninja-jwt.svg)](https://pypi.python.org/pypi/django-ninja-jwt)
[![PyPI version](https://img.shields.io/pypi/djversions/django-ninja-jwt.svg)](https://pypi.python.org/pypi/django-ninja-jwt)
[![Codecov](https://img.shields.io/codecov/c/gh/eadwinCode/django-ninja-jwt)](https://codecov.io/gh/eadwinCode/django-ninja-jwt)
[![Downloads](https://static.pepy.tech/personalized-badge/django-ninja-jwt?period=month&units=international_system&left_color=black&right_color=orange&left_text=Downloads/month)](https://pepy.tech/project/django-ninja-jwt)

## Abstract

Ninja JWT is JSON Web Token plugin for Django-Ninja. The library is a fork of [Simple JWT](https://github.com/jazzband/djangorestframework-simplejwt) by Jazzband, a popular  JWT plugin for [Django REST Framework](http://www.django-rest-framework.org).
#### Notice
This library does not fix any issues from the source SIMPLE JWT. 
It only added support for Django-Ninja and removes DRF dependencies. 
Subsequent updates from SIMPLE JWT will reflect here.

For full documentation, [visit](https://eadwincode.github.io/django-ninja-jwt/).

#### Requirements
- Python >= 3.6
- Django >= 2.1
- Django-Ninja >= 0.16.1
- Ninja-Schema >= 0.12.8
- Django-Ninja-Extra >= 0.14.2

## Example
Checkout this sample project: https://github.com/eadwinCode/bookstoreapi


Installation
============

Ninja JWT can be installed with pip:

    pip install django-ninja-jwt

Also, you need to register `NinjaJWTDefaultController` controller to you Django-Ninja api.
The `NinjaJWTDefaultController` comes with three routes `obtain_token`, `refresh_token` and `verify_token`

```python
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)

```

The `NinjaJWTDefaultController` comes with three routes `obtain_token`, `refresh_token` and `verify_token`. 
It is a combination of two subclass `TokenVerificationController` and `TokenObtainPairController`.
If you wish to customize these routes, you can inherit from these controllers and change its implementation

```python
from ninja_extra import api_controller
from ninja_jwt.controller import TokenObtainPairController

@api_controller('token', tags=['Auth'])
class MyCustomController(TokenObtainPairController):
    """obtain_token and refresh_token only"
...
api.register_controllers(MyCustomController)
```

If you wish to use localizations/translations, simply add `ninja_jwt` to
`INSTALLED_APPS`.

```python
INSTALLED_APPS = [
    ...
    'ninja_jwt',
    ...
]
```

Usage
=====

To verify that Ninja JWT is working, you can use curl to issue a couple
of test requests:

``` {.sourceCode .bash}
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "davidattenborough", "password": "boatymcboatface"}' \
  http://localhost:8000/api/token/pair

...
{
  "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU",
  "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"
}
```

You can use the returned access token to prove authentication for a
protected view:

``` {.sourceCode .bash}
curl \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU" \
  http://localhost:8000/api/some-protected-view/
```

When this short-lived access token expires, you can use the longer-lived
refresh token to obtain another access token:

``` {.sourceCode .bash}
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' \
  http://localhost:8000/api/token/refresh/

...
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNTY3LCJqdGkiOiJjNzE4ZTVkNjgzZWQ0NTQyYTU0NWJkM2VmMGI0ZGQ0ZSJ9.ekxRxgb9OKmHkfy-zs1Ro_xs1eMLXiR17dIDBVxeT-w"}
```
