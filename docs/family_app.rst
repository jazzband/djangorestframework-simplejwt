.. _family_app:

Family app
===========

The **Token Family** system provides a way to group refresh and access tokens into logical families,
allowing developers to track, manage, and invalidate related tokens as a unit.

This feature is especially useful in enhancing security and traceability in authentication flows.
Each token family is identified by a unique ``family_id``, which is included in the token payload.
This enables the system to:

- Detect and respond to refresh token reuse by invalidating the entire token family.
- Revoke all related tokens at once.
- Enforce expiration policies at the family level via a ``family_exp`` claim.

A new token family is automatically created every time a user successfully obtains a pair of tokens
from the ``TokenObtainPairView`` (i.e., when starting a new session). From that point onward, as long as the user
continues to refresh their tokens, the newly issued access and refresh tokens will retain the same
``family_id`` and ``family_exp`` values. This means all tokens issued as part of a session are 
considered to belong to the same token family.

This session-based grouping allows administrators or systems to treat the token family as the unit of trust.
If suspicious activity is detected, the entire session can be invalidated at once by blacklisting the
associated token family.

The Token Family system is optional and customizable. It works best when paired with the
:doc:`/blacklist_app`.

By organizing tokens into families, you gain finer control over user sessions and potential compromises.
For example, when the settings ``BLACKLIST_AFTER_ROTATION`` and ``TOKEN_FAMILY_BLACKLIST_ON_REUSE`` are
set to ``True``, if a refresh token is stolen and used by both the valid user and the attacker,
the system will detect the reuse of the token and automatically blacklist the associated family. 
This invalidates every token that shares the same ``family_id`` as the reused refresh token, effectively
cutting off access without waiting for individual token expiration.

-------

Simple JWT includes an app that provides token family functionality.  To use
this app, include it in your list of installed apps in ``settings.py``:

.. code-block:: python

  # Django project settings.py

  ...

  INSTALLED_APPS = (
      ...
      'rest_framework_simplejwt.token_family',
      ...
  )

Also, make sure to run ``python manage.py migrate`` to run the app's
migrations.

If the token family app is detected in ``INSTALLED_APPS`` and the setting
``TOKEN_FAMILY_ENABLED`` is set to ``True``, Simple JWT will add a new family
to the family list and will also add two new claims, "family_id" and 
"family_exp", to the refresh tokens. It will also check that the
family indicated in the token's payload does not appear in a blacklist of
families before it considers it as valid, and it will also check that the
family expiration date ("family_exp") has not passed; if the family is expired,
then the token will be considered as invalid.

The Simple JWT family app implements its family and blacklisted family
lists using two models: ``TokenFamily`` and ``BlacklistedTokenFamily``.  Model
admins are defined for both of these models.  To add a family to the blacklist,
find its corresponding ``TokenFamily`` record in the admin and use the
admin again to create a ``BlacklistedTokenFamily`` record that points to the
``TokenFamily`` record.

Alternatively, you can blacklist a family by creating a ``FamilyMixin``
subclass instance and calling the instance's ``blacklist_family`` method:

.. code-block:: python

  from rest_framework_simplejwt.tokens import RefreshToken

  token = RefreshToken(base64_encoded_token_string)
  token.blacklist_family()

Keep in mind that the ``base64_encoded_token_string`` should already
contain a family ID claim in its payload.

This will create a unique family and blacklist records for the token's
"family_id" claim or whichever claim is specified by the ``TOKEN_FAMILY_CLAIM`` setting.


In a ``urls.py`` file, you can also include a route for ``TokenFamilyBlacklistView``:

.. code-block:: python

  from rest_framework_simplejwt.views import TokenFamilyBlacklistView

  urlpatterns = [
    ...
    path('api/token/family/blacklist/', TokenFamilyBlacklistView.as_view(), name='token_family_blacklist'),
    ...
  ]

It allows API users to blacklist token families sending them to ``/api/token/family/blacklist/``, for example using curl:

.. code-block:: bash

  curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NzI0OTU1MywiaWF0IjoxNzQ3MjQ0MTUzLCJqdGkiOiI1YmMzMjlmMjVkODE0OGFhOTY1ODI1YjgwNDQ1ZDQ5OCIsInVzZXJfaWQiOjIsImZhbWlseV9pZCI6ImMyZGYyM2M1YjU1NjRmYjNhNTA3MjFhYzVkMTljNThmIiwiZmFtaWx5X2V4cCI6MTc0NzI0OTE1M30.4oDOmtkgot_W2mXByKuCyJLi6_xeMZtDQJmHIBXZx98"}' \
    http://localhost:8000/api/token/family/blacklist/

The family app also provides a management command, ``flushexpiredfamilies``,
which will delete any families from the token family list and family blacklist that have
expired. The command will not affect families that have ``None`` as their expiration.
You should set up a cron job on your server or hosting platform which
runs this command daily.
