.. _multi_session_app:

Multi-session app
=================
.. note::

 Multi-session support is available only when using TokenObtainPair.
 It is not compatible with Sliding tokens or other stateless authentication
 methods, since those tokens cannot be reliably associated with a server-side session.

Simple JWT can be extended with an app that provides **multi-device session
support**. This allows users to maintain multiple active sessions across
different devices while keeping the ability to manage or revoke them.

To use this app, include it in your list of installed apps in ``settings.py``:

.. code-block:: python

  # Django project settings.py

  ...

  INSTALLED_APPS = (
      ...
      'rest_framework_simplejwt.jwt_multi_session',
      ...
  )

Also, make sure to run ``python manage.py migrate`` to run the app's
migrations.

If the multi-session app is detected in ``INSTALLED_APPS`` and the setting
``ALLOW_MULTI_DEVICE`` is enabled, Simple JWT will automatically create
a ``JWTSession`` object for every login. The session will be bound to the
RefreshToken’s ``jti`` claim and validated on every request.

The multi-session app implements its functionality using a model:
``JWTSession``. Each session stores:

- The user  
- A unique session ID (UUID, used as ``jti``)  
- Device User-Agent  
- Device IP  
- Creation and expiry timestamps  

To add multi-session support, enable the flag in your settings:

.. code-block:: python

  SIMPLE_JWT = {
      "ALLOW_MULTI_DEVICE": True,
  }

A session is created automatically whenever a user obtains a token pair (access and refresh).

Authentication
--------------

The app provides a custom authentication class, ``JWTAuthentication``,
which validates tokens against their server-side session:

If a session has expired or has been deleted, authentication will fail with
``AuthenticationFailed``. This prevents reuse of AccessTokens and RefreshTokens  that no longer
belong to a valid session.

Accessing the current session
-----------------------------

When authentication succeeds, ``JWTAuthentication`` returns ``(user, session)``.  
The active session can be accessed in your views as ``request.auth``.

Example::

   session = request.auth
   print(session.id)  # session_id



Managing sessions
-----------------

The app provides a ``SessionsView`` which allows API users to list or revoke
their sessions.

Because ``SessionsView`` is a viewset we need to add router


Example ``urls.py``:

.. code-block:: python

  from jwt_multi_session.views import SessionsView
  from rest_framework.routers import DefaultRouter

  router = DefaultRouter()
  router.register('sessions', SessionsView, basename='sessions')

  urlpatterns = [
      ...
      path('', include(router.urls)),
      ...
  ]

Example usage (list sessions):

.. code-block:: bash

  curl -H "Authorization: Bearer <access_token>" \
    http://localhost:8000/api/sessions/

Response:

.. code-block:: json

  [
    {
      "id": "e6a8fa23-45f4-4c79-a9a2-739fddaa57d7",
      "device_agent": "Mozilla/5.0",
      "device_ip": "192.168.1.10",
      "created_at": "2025-08-29T08:30:00Z",
      "expired_at": "2025-08-30T08:30:00Z"
    }
  ]

Revoke (delete) a session:

.. code-block:: bash

  curl -X DELETE \
    -H "Authorization: Bearer <access_token>" \
    http://localhost:8000/api/sessions/e6a8fa23-45f4-4c79-a9a2-739fddaa57d7/


Lifecycle
---------

1. **Login** → A new ``JWTSession`` is created and bound to the RefreshToken.  
2. **Authenticate request** → ``JWTAuthentication`` validates the token against the session.  
3. **Session expiration** → Session expires based on ``REFRESH_TOKEN_LIFETIME``.  
4. **Revoke/Delete session** → User can remove active sessions via the API.  

This allows secure management of JWTs across multiple devices while retaining
server-side control.
