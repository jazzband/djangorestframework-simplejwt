from __future__ import unicode_literals

from datetime import datetime

from django.utils.six import text_type, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .exceptions import TokenError, TokenBackendError
from .settings import api_settings
from .utils import datetime_to_epoch, format_lazy


@python_2_unicode_compatible
class Token(object):
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """
    def __init__(self, token=None):
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        self.token = token

        # Set up token
        if token is not None:
            # An encoded token was provided
            from .state import token_backend

            # Ensure token and signature are valid
            try:
                self.payload = token_backend.decode(token)
            except TokenBackendError:
                raise TokenError(_('Token is invalid or expired'))

            # According to RFC 7519, the "exp" claim is OPTIONAL
            # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
            # correct behavior for authorization tokens, we require an "exp"
            # claim.  We don't want any zombie tokens walking around.
            self.check_exp()
        else:
            self.payload = {}

    def __repr__(self):
        return repr(self.payload)

    def __getitem__(self, name):
        return self.payload[name]

    def __setitem__(self, name, value):
        self.payload[name] = value

    def __contains__(self, name):
        return name in self.payload

    def __str__(self):
        """
        Signs and returns a token as a base64 encoded string.
        """
        from .state import token_backend

        return token_backend.encode(self.payload)

    def set_exp(self, claim='exp', from_time=None, lifetime=None):
        """
        Updates the expiration time of a token.
        """
        if from_time is None:
            from_time = datetime.utcnow()

        if lifetime is None:
            lifetime = api_settings.TOKEN_LIFETIME

        self.payload[claim] = datetime_to_epoch(from_time + lifetime)

    def check_exp(self, claim='exp', current_time=None):
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = datetime.utcnow()

        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim))

        claim_time = datetime.utcfromtimestamp(claim_value)
        if claim_time < current_time:
            raise TokenError(format_lazy(_("Token '{}' claim has expired"), claim))

    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = text_type(user_id)

        token = cls()
        token[api_settings.USER_ID_CLAIM] = user_id

        now = datetime.utcnow()
        token.set_exp(from_time=now)
        token.set_exp('refresh_exp', from_time=now, lifetime=api_settings.TOKEN_REFRESH_LIFETIME)

        return token
