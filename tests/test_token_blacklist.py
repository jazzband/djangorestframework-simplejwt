from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from mock import patch
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken, OutstandingToken
)
from rest_framework_simplejwt.tokens import (
    AccessToken, RefreshToken, SlidingToken
)
from rest_framework_simplejwt.utils import aware_utcnow, datetime_from_epoch


class TestTokenBlacklist(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test_user',
            password='test_password',
        )

    def test_sliding_tokens_are_added_to_outstanding_list(self):
        token = SlidingToken.for_user(self.user)

        qs = OutstandingToken.objects.all()
        outstanding_token = qs.first()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(outstanding_token.user, self.user)
        self.assertEqual(outstanding_token.jti, token['jti'])
        self.assertEqual(outstanding_token.token, str(token))
        self.assertEqual(outstanding_token.created_at, token.current_time)
        self.assertEqual(outstanding_token.expires_at, datetime_from_epoch(token['exp']))

    def test_refresh_tokens_are_added_to_outstanding_list(self):
        token = RefreshToken.for_user(self.user)

        qs = OutstandingToken.objects.all()
        outstanding_token = qs.first()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(outstanding_token.user, self.user)
        self.assertEqual(outstanding_token.jti, token['jti'])
        self.assertEqual(outstanding_token.token, str(token))
        self.assertEqual(outstanding_token.created_at, token.current_time)
        self.assertEqual(outstanding_token.expires_at, datetime_from_epoch(token['exp']))

    def test_access_tokens_are_not_added_to_outstanding_list(self):
        AccessToken.for_user(self.user)

        qs = OutstandingToken.objects.all()

        self.assertFalse(qs.exists())

    def test_token_will_not_validate_if_blacklisted(self):
        token = RefreshToken.for_user(self.user)
        outstanding_token = OutstandingToken.objects.first()

        # Should raise no exception
        RefreshToken(str(token))

        # Add token to blacklist
        BlacklistedToken.objects.create(token=outstanding_token)

        with self.assertRaises(TokenError) as e:
            # Should raise exception
            RefreshToken(str(token))
            self.assertIn('blacklisted', e.exception.args[0])


class TestTokenBlacklistFlushExpiredTokens(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test_user',
            password='test_password',
        )

    def test_it_should_delete_any_expired_tokens(self):
        # Make some tokens that won't expire soon
        not_expired_1 = RefreshToken.for_user(self.user)
        not_expired_2 = RefreshToken.for_user(self.user)

        # Blacklist a fresh token
        token = OutstandingToken.objects.get(jti=not_expired_2['jti'])
        BlacklistedToken.objects.create(token=token)

        # Make tokens with fake exp time that will expire soon
        fake_now = aware_utcnow() - api_settings.REFRESH_TOKEN_LIFETIME

        with patch('rest_framework_simplejwt.tokens.aware_utcnow') as fake_aware_utcnow:
            fake_aware_utcnow.return_value = fake_now

            RefreshToken.for_user(self.user)
            expired = RefreshToken.for_user(self.user)

        # Blacklist an expired token
        token = OutstandingToken.objects.get(jti=expired['jti'])
        BlacklistedToken.objects.create(token=token)

        # Make another token that won't expire soon
        not_expired_3 = RefreshToken.for_user(self.user)

        # Should be 5 outstanding tokens and 2 blacklisted tokens
        self.assertEqual(OutstandingToken.objects.count(), 5)
        self.assertEqual(BlacklistedToken.objects.count(), 2)

        call_command('flushexpiredtokens')

        # Expired outstanding *and* blacklisted tokens should be gone
        self.assertEqual(OutstandingToken.objects.count(), 3)
        self.assertEqual(BlacklistedToken.objects.count(), 1)

        self.assertEqual(
            [i.jti for i in OutstandingToken.objects.all()],
            [not_expired_1['jti'], not_expired_2['jti'], not_expired_3['jti']],
        )
        self.assertEqual(
            BlacklistedToken.objects.first().token.jti,
            not_expired_2['jti'],
        )
