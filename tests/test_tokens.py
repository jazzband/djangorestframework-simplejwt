from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from jose import jwt

from ninja_jwt.exceptions import TokenError
from ninja_jwt.settings import api_settings
from ninja_jwt.state import token_backend
from ninja_jwt.tokens import (
    AccessToken,
    RefreshToken,
    SlidingToken,
    Token,
    UntypedToken,
)
from ninja_jwt.utils import aware_utcnow, datetime_to_epoch, make_utc

from .utils import override_api_settings

User = get_user_model()


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestToken:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.token = MyToken()

    def test_init_no_token_type_or_lifetime(self):
        class MyTestToken(Token):
            pass

        with pytest.raises(TokenError):
            MyTestToken()

        MyTestToken.token_type = "test"

        with pytest.raises(TokenError):
            MyTestToken()

        del MyTestToken.token_type
        MyTestToken.lifetime = timedelta(days=1)

        with pytest.raises(TokenError):
            MyTestToken()

        MyTestToken.token_type = "test"
        MyTestToken()

    def test_init_no_token_given(self):
        now = make_utc(datetime(year=2000, month=1, day=1))

        with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            t = MyToken()

        assert t.current_time == now
        assert t.token is None

        assert len(t.payload) == 4
        assert t.payload["exp"] == datetime_to_epoch(now + MyToken.lifetime)
        assert t.payload["iat"] == datetime_to_epoch(now)
        assert "jti" in t.payload
        assert t.payload[api_settings.TOKEN_TYPE_CLAIM] == MyToken.token_type

    def test_init_token_given(self):
        # Test successful instantiation
        original_now = aware_utcnow()

        with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = original_now
            good_token = MyToken()

        good_token["some_value"] = "arst"
        encoded_good_token = str(good_token)

        now = aware_utcnow()

        # Create new token from encoded token
        with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            # Should raise no exception
            t = MyToken(encoded_good_token)

        # Should have expected properties
        assert t.current_time == now
        assert t.token == encoded_good_token

        assert len(t.payload) == 5
        assert t["some_value"] == "arst"
        assert t["exp"] == datetime_to_epoch(original_now + MyToken.lifetime)
        assert t["iat"] == datetime_to_epoch(original_now)
        assert t[api_settings.TOKEN_TYPE_CLAIM] == MyToken.token_type
        assert "jti" in t.payload

    def test_init_bad_sig_token_given(self):
        # Test backend rejects encoded token (expired or bad signature)
        payload = {"foo": "bar"}
        payload["exp"] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(payload, api_settings.SIGNING_KEY, algorithm="HS256")
        payload["foo"] = "baz"
        token_2 = jwt.encode(payload, api_settings.SIGNING_KEY, algorithm="HS256")

        token_2_payload = token_2.rsplit(".", 1)[0]
        token_1_sig = token_1.rsplit(".", 1)[-1]
        invalid_token = token_2_payload + "." + token_1_sig

        with pytest.raises(TokenError):
            MyToken(invalid_token)

    def test_init_bad_sig_token_given_no_verify(self):
        # Test backend rejects encoded token (expired or bad signature)
        payload = {"foo": "bar"}
        payload["exp"] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(payload, api_settings.SIGNING_KEY, algorithm="HS256")
        payload["foo"] = "baz"
        token_2 = jwt.encode(payload, api_settings.SIGNING_KEY, algorithm="HS256")

        token_2_payload = token_2.rsplit(".", 1)[0]
        token_1_sig = token_1.rsplit(".", 1)[-1]
        invalid_token = token_2_payload + "." + token_1_sig

        t = MyToken(invalid_token, verify=False)

        assert t.payload == payload

    def test_init_expired_token_given(self):
        t = MyToken()
        t.set_exp(lifetime=-timedelta(seconds=1))

        with pytest.raises(TokenError):
            MyToken(str(t))

    def test_init_no_type_token_given(self):
        t = MyToken()
        del t[api_settings.TOKEN_TYPE_CLAIM]

        with pytest.raises(TokenError):
            MyToken(str(t))

    def test_init_wrong_type_token_given(self):
        t = MyToken()
        t[api_settings.TOKEN_TYPE_CLAIM] = "wrong_type"

        with pytest.raises(TokenError):
            MyToken(str(t))

    def test_init_no_jti_token_given(self):
        t = MyToken()
        del t["jti"]

        with pytest.raises(TokenError):
            MyToken(str(t))

    def test_str(self):
        token = MyToken()
        token.set_exp(
            from_time=make_utc(datetime(year=2000, month=1, day=1)),
            lifetime=timedelta(seconds=0),
        )

        # Delete all but one claim.  We want our lives to be easy and for there
        # to only be a couple of possible encodings.  We're only testing that a
        # payload is successfully encoded here, not that it has specific
        # content.
        del token[api_settings.TOKEN_TYPE_CLAIM]
        del token["jti"]
        del token["iat"]

        # Should encode the given token
        encoded_token = str(token)

        # Token could be one of two depending on header dict ordering
        assert encoded_token in (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.VKoOnMgmETawjDZwxrQaHG0xHdo6xBodFy6FXJzTVxs",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.iqxxOHV63sjeqNR1GDxX3LPvMymfVB76sOIDqTbjAgk",
        )

    def test_repr(self):
        assert repr(self.token) == repr(self.token.payload)

    def test_getitem(self):
        assert self.token["exp"] == self.token.payload["exp"]

    def test_setitem(self):
        self.token["test"] = 1234
        assert self.token.payload["test"] == 1234

    def test_delitem(self):
        self.token["test"] = 1234
        assert self.token.payload["test"] == 1234

        del self.token["test"]
        assert "test" not in self.token

    def test_contains(self):
        assert "exp" in self.token

    def test_get(self):
        self.token["test"] = 1234

        assert 1234 == self.token.get("test")
        assert 1234 == self.token.get("test", 2345)

        assert self.token.get("does_not_exist") is None
        assert 1234 == self.token.get("does_not_exist", 1234)

    def test_set_jti(self):
        token = MyToken()
        old_jti = token["jti"]

        token.set_jti()

        assert "jti" in token
        assert old_jti != token["jti"]

    def test_set_exp(self):
        now = make_utc(datetime(year=2000, month=1, day=1))

        token = MyToken()
        token.current_time = now

        # By default, should add 'exp' claim to token using `self.current_time`
        # and the TOKEN_LIFETIME setting
        token.set_exp()
        assert token["exp"] == datetime_to_epoch(now + MyToken.lifetime)

        # Should allow overriding of beginning time, lifetime, and claim name
        token.set_exp(claim="refresh_exp", from_time=now, lifetime=timedelta(days=1))
        assert "refresh_exp" in token
        assert token["refresh_exp"] == datetime_to_epoch(now + timedelta(days=1))

    def test_set_iat(self):
        now = make_utc(datetime(year=2000, month=1, day=1))

        token = MyToken()
        token.current_time = now

        # By default, should add 'iat' claim to token using `self.current_time`
        token.set_iat()
        assert token["iat"] == datetime_to_epoch(now)

        # Should allow overriding of time and claim name
        token.set_iat(claim="refresh_iat", at_time=now + timedelta(days=1))
        assert "refresh_iat" in token
        assert token["refresh_iat"] == datetime_to_epoch(now + timedelta(days=1))

    def test_check_exp(self):
        token = MyToken()

        # Should raise an exception if no claim of given kind
        with pytest.raises(TokenError):
            token.check_exp("non_existent_claim")

        current_time = token.current_time
        lifetime = timedelta(days=1)
        exp = token.current_time + lifetime

        token.set_exp(lifetime=lifetime)

        # By default, checks 'exp' claim against `self.current_time`.  Should
        # raise an exception if claim has expired.
        token.current_time = exp
        with pytest.raises(TokenError):
            token.check_exp()

        token.current_time = exp + timedelta(seconds=1)
        with pytest.raises(TokenError):
            token.check_exp()

        # Otherwise, should raise no exception
        token.current_time = current_time
        token.check_exp()

        # Should allow specification of claim to be examined and timestamp to
        # compare against

        # Default claim
        with pytest.raises(TokenError):
            token.check_exp(current_time=exp)

        token.set_exp("refresh_exp", lifetime=timedelta(days=1))

        # Default timestamp
        token.check_exp("refresh_exp")

        # Given claim and timestamp
        with pytest.raises(TokenError):
            token.check_exp(
                "refresh_exp", current_time=current_time + timedelta(days=1)
            )
        with pytest.raises(TokenError):
            token.check_exp(
                "refresh_exp", current_time=current_time + timedelta(days=2)
            )

    def test_check_token_not_expired_if_in_leeway(self):
        token = MyToken()
        token.set_exp("refresh_exp", lifetime=timedelta(days=1))

        datetime_in_leeway = token.current_time + timedelta(days=1)

        with pytest.raises(TokenError):
            token.check_exp("refresh_exp", current_time=datetime_in_leeway)

        # a token 1 day expired is valid if leeway is 2 days
        token.token_backend.leeway = timedelta(days=2).total_seconds()
        token.check_exp("refresh_exp", current_time=datetime_in_leeway)
        token.token_backend.leeway = 0

    @pytest.mark.django_db
    def test_for_user(self, monkeypatch):
        username = "test_user"
        user = User.objects.create_user(
            username=username,
            password="test_password",
        )

        token = MyToken.for_user(user)

        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        assert token[api_settings.USER_ID_CLAIM] == user_id

        # Test with non-int user id
        with monkeypatch.context() as m:
            m.setattr(api_settings, "USER_ID_FIELD", "username")
            token = MyToken.for_user(user)

        assert token[api_settings.USER_ID_CLAIM] == username

    def test_get_token_backend(self):
        token = MyToken()

        assert token.get_token_backend() == token_backend


class TestSlidingToken:
    def test_init(self):
        # Should set sliding refresh claim and token type claim
        token = SlidingToken()

        assert token[api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM] == datetime_to_epoch(
            token.current_time + api_settings.SLIDING_TOKEN_REFRESH_LIFETIME
        )

        assert token[api_settings.TOKEN_TYPE_CLAIM] == "sliding"


class TestAccessToken:
    def test_init(self):
        # Should set token type claim
        token = AccessToken()
        assert token[api_settings.TOKEN_TYPE_CLAIM] == "access"


class TestRefreshToken:
    def test_init(self):
        # Should set token type claim
        token = RefreshToken()
        assert token[api_settings.TOKEN_TYPE_CLAIM] == "refresh"

    def test_access_token(self):
        # Should create an access token from a refresh token
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        access = refresh.access_token

        assert isinstance(access, AccessToken)
        assert access[api_settings.TOKEN_TYPE_CLAIM] == "access"

        # Should keep all copyable claims from refresh token
        assert refresh["test_claim"] == access["test_claim"]

        # Should not copy certain claims from refresh token
        for claim in RefreshToken.no_copy_claims:
            assert refresh[claim] != access[claim]


class TestUntypedToken:
    def test_it_should_accept_and_verify_any_type_of_token(self):
        access_token = AccessToken()
        refresh_token = RefreshToken()
        sliding_token = SlidingToken()

        for t in (access_token, refresh_token, sliding_token):
            untyped_token = UntypedToken(str(t))

            assert t.payload == untyped_token.payload

    def test_it_should_expire_immediately_if_made_from_scratch(self):
        t = UntypedToken()

        assert t[api_settings.TOKEN_TYPE_CLAIM] == "untyped"

        with pytest.raises(TokenError):
            t.check_exp()
