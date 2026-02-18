.. _cookie_authentication:

Cookie-based Authentication
===============================

Overview
--------

``JWTCookieAuthentication`` is an optional authentication backend that
authenticates JSON Web Tokens (JWTs) **exclusively from HttpOnly cookies**.

Unlike ``JWTAuthentication``, this backend **does not read tokens from the
Authorization header**. Instead, it expects JWTs to already be present in
cookies attached to the incoming request.

This authentication method is intended for browser-based applications
where storing JWTs in HttpOnly cookies is preferred over exposing tokens
to JavaScript.

---

How it works
------------

The ``JWTCookieAuthentication`` backend behaves as follows:

* Reads the JWT from a configured cookie (default: ``access``)
* If the cookie is missing, authentication is skipped
* If the cookie contains an invalid or expired token, authentication fails
* The Authorization header is intentionally ignored

This backend only handles **authentication**. It does not issue tokens
or set cookies.

---

Enabling cookie authentication
------------------------------

To enable cookie-based authentication, configure Django REST Framework
to use ``JWTCookieAuthentication``:

.. code-block:: python

    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTCookieAuthentication",
        ),
    }

Configure the cookie name using ``SIMPLE_JWT`` settings:

.. code-block:: python

    SIMPLE_JWT = {
        "AUTH_COOKIE": "access",
    }

---

Token issuance and login
------------------------

``JWTCookieAuthentication`` **does not create or set cookies**.

The default SimpleJWT token views (``TokenObtainPairView`` and
``TokenRefreshView``) return tokens in the response body and **do not store
tokens in cookies**.

When using cookie-based authentication, JWTs **must already be present in
cookies**. This typically requires using **cookie-aware login and refresh
views** that store tokens in HttpOnly cookies.

Example of setting a cookie after successful authentication:

.. code-block:: python

    response.set_cookie(
        "access",
        access_token,
        max_age=3600,
        path="/",
        secure=True,
        httponly=True,
        samesite="Lax",
    )

The responsibility for issuing tokens and setting cookies lies outside
of this authentication backend.

---

Refresh tokens
--------------

If refresh tokens are used with cookie-based authentication, they should
also be stored in HttpOnly cookies and handled by cookie-aware refresh
views.

The default ``TokenRefreshView`` expects refresh tokens in the request
body and does not read cookies.

---

Security considerations
-----------------------

When using cookie-based JWT authentication, the following security
requirements apply:

* Cookies **must** be marked ``HttpOnly`` to prevent access from JavaScript
* Cookies **should** be marked ``Secure`` when used over HTTPS
* CSRF protection **must be enabled** for unsafe HTTP methods
* This backend is recommended only for browser-based clients

Failure to enforce CSRF protection when using cookies may expose the
application to cross-site request forgery attacks.

---

When to use this backend
-----------------------

Use ``JWTCookieAuthentication`` if:

* You are building a browser-based application
* You want to avoid storing JWTs in JavaScript-accessible storage
* You prefer HttpOnly cookie-based authentication

Do **not** use this backend if:

* You rely on Authorization headers for authentication
* You are building APIs intended for third-party clients
* You require stateless, header-only authentication
