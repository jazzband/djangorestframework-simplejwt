.. _token_types:

Token types
===========

Ninja JWT provides two different token types that can be used to prove
authentication.  In a token's payload, its type can be identified by the value
of its token type claim, which is "token_type" by default.  This may have a
value of "access", "sliding", or "refresh" however refresh tokens are not
considered valid for authentication at this time.  The claim name used to store
the type can be customized by changing the ``TOKEN_TYPE_CLAIM`` setting.

By default, Ninja JWT expects an "access" token to prove authentication.  The
allowed auth token types are determined by the value of the
``AUTH_TOKEN_CLASSES`` setting.  This setting contains a list of dot paths to
token classes.  It includes the
``'ninja_jwt.tokens.AccessToken'`` dot path by default but may
also include the ``'ninja_jwt.tokens.SlidingToken'`` dot path.
Either or both of those dot paths may be present in the list of auth token
classes.  If they are both present, then both of those token types may be used
to prove authentication.

Sliding tokens
--------------

Sliding tokens offer a more convenient experience to users of tokens with the
trade-offs of being less secure and, in the case that the blacklist app is
being used, less performant.  A sliding token is one which contains both an
expiration claim and a refresh expiration claim.  As long as the timestamp in a
sliding token's expiration claim has not passed, it can be used to prove
authentication.  Additionally, as long as the timestamp in its refresh
expiration claim has not passed, it may also be submitted to a refresh view to
get another copy of itself with a renewed expiration claim.

If you want to use sliding tokens, change the ``AUTH_TOKEN_CLASSES`` setting to
``('ninja_jwt.tokens.SlidingToken',)``.  (Alternatively, the
``AUTH_TOKEN_CLASSES`` setting may include dot paths to both the
``AccessToken`` and ``SlidingToken`` token classes in the
``ninja_jwt.tokens`` module if you want to allow both token
types to be used for authentication.)

Also, include urls for the sliding token specific ``TokenObtainSlidingView``
and ``TokenRefreshSlidingView`` views alongside or in place of urls for the
access token specific ``TokenObtainPairView`` and ``TokenRefreshView`` views:

.. code-block:: python

  from ninja_jwt.views import (
      TokenObtainSlidingView,
      TokenRefreshSlidingView,
  )

  urlpatterns = [
      ...
      path('api/token/', TokenObtainSlidingView.as_view(), name='token_obtain'),
      path('api/token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
      ...
  ]

Be aware that, if you are using the blacklist app, Ninja JWT will validate all
sliding tokens against the blacklist for each authenticated request.  This will
reduce the performance of authenticated API views.
