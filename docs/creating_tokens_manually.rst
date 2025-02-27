.. _creating_tokens_manually:

Creating tokens manually
========================

Sometimes, you may wish to manually create a token for a user.  This could be
done as follows:

.. warning::
    The ``for_user`` method does not check if the user is active. If you need to verify the user's status,
    this check needs to be done before creating the tokens.

.. code-block:: python

  from rest_framework_simplejwt.tokens import RefreshToken
  from rest_framework_simplejwt.exceptions import AuthenticationFailed

  def get_tokens_for_user(user):
      if not user.is_active:
        raise AuthenticationFailed("User is not active")

      refresh = RefreshToken.for_user(user)

      return {
          'refresh': str(refresh),
          'access': str(refresh.access_token),
      }

The above function ``get_tokens_for_user`` will return the serialized
representations of new refresh and access tokens for the given user.  In
general, a token for any subclass of ``rest_framework_simplejwt.tokens.Token``
can be created in this way.
