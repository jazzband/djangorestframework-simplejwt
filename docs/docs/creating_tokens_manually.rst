.. _creating_tokens_manually:

Creating tokens manually
========================

Sometimes, you may wish to manually create a token for a user.  This could be
done as follows:

.. code-block:: python

  from ninja_jwt.tokens import RefreshToken

  def get_tokens_for_user(user):
      refresh = RefreshToken.for_user(user)

      return {
          'refresh': str(refresh),
          'access': str(refresh.access_token),
      }

The above function ``get_tokens_for_user`` will return the serialized
representations of new refresh and access tokens for the given user.  In
general, a token for any subclass of ``ninja_jwt.tokens.Token``
can be created in this way.
