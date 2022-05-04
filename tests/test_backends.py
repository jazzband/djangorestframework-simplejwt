import uuid
from datetime import datetime, timedelta
from json import JSONEncoder
from unittest import mock
from unittest.mock import patch

import jwt
import pytest
from django.test import TestCase
from jwt import PyJWS
from jwt import __version__ as jwt_version
from jwt import algorithms

from rest_framework_simplejwt.backends import JWK_CLIENT_AVAILABLE, TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.utils import aware_utcnow, datetime_to_epoch, make_utc
from tests.keys import (
    ES256_PRIVATE_KEY,
    ES256_PUBLIC_KEY,
    PRIVATE_KEY,
    PRIVATE_KEY_2,
    PUBLIC_KEY,
    PUBLIC_KEY_2,
)

SECRET = "not_secret"

AUDIENCE = "openid-client-id"

ISSUER = "https://www.myoidcprovider.com"

JWK_URL = "https://randomstring.auth0.com/.well-known/jwks.json"

LEEWAY = 100

IS_OLD_JWT = jwt_version == "1.7.1"


class UUIDJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class TestTokenBackend(TestCase):
    def setUp(self):
        self.hmac_token_backend = TokenBackend("HS256", SECRET)
        self.hmac_leeway_token_backend = TokenBackend("HS256", SECRET, leeway=LEEWAY)
        self.rsa_token_backend = TokenBackend("RS256", PRIVATE_KEY, PUBLIC_KEY)
        self.aud_iss_token_backend = TokenBackend(
            "RS256", PRIVATE_KEY, PUBLIC_KEY, AUDIENCE, ISSUER
        )
        self.payload = {"foo": "bar"}
        self.backends = (
            self.hmac_token_backend,
            self.rsa_token_backend,
            TokenBackend("ES256", ES256_PRIVATE_KEY, ES256_PUBLIC_KEY),
            TokenBackend("ES384", ES256_PRIVATE_KEY, ES256_PUBLIC_KEY),
            TokenBackend("ES512", ES256_PRIVATE_KEY, ES256_PUBLIC_KEY),
        )

    def test_init(self):
        # Should reject unknown algorithms
        with self.assertRaises(TokenBackendError):
            TokenBackend("oienarst oieanrsto i", "not_secret")

        TokenBackend("HS256", "not_secret")

    @patch.object(algorithms, "has_crypto", new=False)
    def test_init_fails_for_rs_algorithms_when_crypto_not_installed(self):
        for algo in ("RS256", "RS384", "RS512", "ES256"):
            with self.assertRaisesRegex(
                TokenBackendError,
                f"You must have cryptography installed to use {algo}.",
            ):
                TokenBackend(algo, "not_secret")

    def test_encode_hmac(self):
        # Should return a JSON web token for the given payload
        payload = {"exp": make_utc(datetime(year=2000, month=1, day=1))}

        hmac_token = self.hmac_token_backend.encode(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            hmac_token,
            (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.NHpdD2X8ub4SE_MZLBedWa57FCpntGaN_r6f8kNKdUs",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.jvxQgXCSDToR8uKoRJcMT-LmMJJn2-NM76nfSR2FOgs",
            ),
        )

    def test_encode_rsa(self):
        # Should return a JSON web token for the given payload
        payload = {"exp": make_utc(datetime(year=2000, month=1, day=1))}

        rsa_token = self.rsa_token_backend.encode(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            rsa_token,
            (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.cuE6ocmdxVHXVrGufzn-_ZbXDV475TPPb5jtSacvJsnR3s3tLIm9yR7MF4vGcCAUGJn2hU_JgSOhs9sxntPPVjdwvC3-sxAwfUQ5AgUCEAF5XC7wTvGhmvufzhAgEG_DNsactCh79P8xRnc0iugtlGNyFp_YK582-ZrlfQEp-7C0L9BNG_JCS2J9DsGR7ojO2xGFkFfzezKRkrVTJMPLwpl0JAiZ0iqbQE-Tex7redCrGI388_mgh52GLsNlSIvW2gQMqCVMYndMuYx32Pd5tuToZmLUQ2PJ9RyAZ4fOMApTzoshItg4lGqtnt9CDYzypHULJZohJIPcxFVZZfHxhw",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.pzHTOaVvKJMMkSqksGh-NdeEvQy8Thre3hBM3smUW5Sohtg77KnHpaUYjq30DyRmYQRmPSjEVprh1Yvic_-OeAXPW8WVsF-r4YdJuxWUpuZbIPwJ9E-cMfTZkDkOl18z1zOdlsLtsP2kXyAlptyy9QQsM7AxoqM6cyXoQ5TI0geWccgoahTy3cBtA6pmjm7H0nfeDGqpqYQBhtaFmRuIWn-_XtdN9C6NVmRCcZwyjH-rP3oEm6wtuKJEN25sVWlZm8YRQ-rj7A7SNqBB5tFK2anM_iv4rmBlIEkmr_f2s_WqMxn2EWUSNeqbqiwabR6CZUyJtKx1cPG0B2PqOTcZsg",
            ),
        )

    def test_encode_aud_iss(self):
        # Should return a JSON web token for the given payload
        original_payload = {"exp": make_utc(datetime(year=2000, month=1, day=1))}
        payload = original_payload.copy()

        rsa_token = self.aud_iss_token_backend.encode(payload)

        # Assert that payload has not been mutated by the encode() function
        self.assertEqual(payload, original_payload)

        # Token could be one of 12 depending on header dict ordering
        self.assertIn(
            rsa_token,
            (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCIsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.kSz7KyUZgpKaeQHYSQlhsE-UFLG2zhBiJ2MFCIvhstA4lSIKj3U1fdP1OhEDg7X66EquRRIZrby6M7RncqCdsjRwKrEIaL74KgC4s5PDXa_HC6dtpi2GhXqaLz8YxfCPaNGZ_9q9rs4Z4O6WpwBLNmMQrTxNno9p0uT93Z2yKj5hGih8a9C_CSf_rKtsHW9AJShWGoKpR6qQFKVNP1GAwQOQ6IeEvZenq_LSEywnrfiWp4Y5UF7xi42wWx7_YPQtM9_Bp5sB-DbrKg_8t0zSc-OHeVDgH0TKqygGEea09W0QkmJcROkaEbxt2LxJg9OuSdXgudVytV8ewpgNtWNE4g",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMCwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.l-sJR5VKGKNrEn5W8sfO4tEpPq4oQ-Fm5ttQyqUkF6FRJHmCfS1TZIUSXieDLHmarnb4hdIGLr5y-EAbykiqYaTn8d25oT2_zIPlCYHt0DxxeuOliGad5l3AXbWee0qPoZL7YCV8FaSdv2EjtMDOEiJBG5yTkaqZlRmSkbfqu1_y2DRErv3X5LpfEHuKoum4jv5YpoCS6wAWDaWJ9cXMPQaGc4gXg4cuSQxb_EjiQ3QYyztHhG37gOu1J-r_rudaiiIk_VZQdYNfCcirp8isS0z2dcNij_0bELp_oOaipsF7uwzc6WfNGR7xP50X1a_K6EBZzVs0eXFxvl9b3C_d8A",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDAsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.aTwQEIxSzhI5fN4ffQMzZ6h61Ur-Gzh_gPkgOyyWvMX890Z18tC2RisEjXeL5xDGKe2XiEAVtuJa9CjXB9eJoCxNN1k05C-ph82cco-0m_TbMbs0d1MFnfC9ESr4JKynP_Klxi8bi0iZMazduT15pH4UhRkEGsnp8rOKtlt_8_8UOGBJAzG34161lM4JbZqrZDit1DvQdGxaC0lmMgosKg3NDMECfkPe3pGLJ5F_su5yhQk0xyKNCjYyE2FNlilWoDV2KkGiCWdsFOgRMAJwHZ-cdgPg8Vyh2WthBNblsbRVfDrGtfPX0VuW5B0RhBhvI5Iut34P9kkxKRFo3NaiEg",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiZXhwIjo5NDY2ODQ4MDB9.w46s7u28LgsnmK6K_5O15q1SFkKeRgkkplFLi5idq1z7qJjXUi45qpXIyQw3W8a0k1fwa22WB_0XC1MTo22OK3Z0aGNCI2ZCBxvZGOAc1WcCUae44a9LckPHp80q0Hs03NvjsuRVLGXRwDVHrYxuGnFxQSEMbZ650-MQkfVFIXVzMOOAn5Yl4ntjigLcw8iPEqJPnDLdFUSnObZjRzK1M6mJf0-125pqcFsCJaa49rjdbTtnN-VuGnKmv9wV1GwevRQPWjx2vinETURVO9IyZCDtdaLJkvL7Z5IpToK5jrZPc1UWAR0VR8WeWfussFoHzJF86LxVxnqIeXnqOhq5SQ",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDB9.Np_SJYye14vz0cvALvfYNqZXvXMD_gY6kIaxA458kbeu6veC_Ds45uWgjJFhTSYFAFWd3TB6M7qZbWgiO0ycION2-B9Yfgaf82WzNtPfgDhu51w1cbLnvuOSRvgX69Q6Z2i1SByewKaSDw25BaMv9Ty4DBdoCbG62qELnNKjDSQvuHlz8cRJv2I6xJBeOYgZV-YN8Zmxsles44a57Vvcj-DjVouHj5m4LperIxb9islNUQBPRTbvw1d_tR8O8ny0mQqbsWL7e2J-wfwdduVf1kVCPePkhHMM6GLhPIrSoTgMzZuRYLBJ61yphuDK98zTknNBM-Jtn5cMyBwP9JBJvA",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.KJcWZtEluPrkRbYj2i_QmdWpZqGZt63Q8nO4QAJ4B4418ZfmgB6A54_vUmWd3Xc18DYgReLoNPlaOuRXtR7rzlMk0-ADjV0bsca5NwTNAV2F-gR9Xsr9iFlcPMNAYf4CAs85gg7deMIxlbGTAaoft__58ah2_vdd8o_nem1PdzsPC198AYtcwnIV206qpeCNR8S_ZTU46OaHwCoySVRx9E7tNG13YSCmGvBaEqgQHKH82qLXo0KivFrjGmGP0xePFG1B8HCZl-LH1euXGGCp6S48q-tmepX5GJwvzaZNBam4pfxQ0GIHa7z11e7sEN-196iDPCK8NzDcXFwHOAnyaA",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCIsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.MfhVcFN-9Rd0j11CLtxopzREKdyJH1loSpD4ibjP6Aco4-iM5C99B6gliPgOldtuevhneXV2I7NGhmZFULaYhulcLrAgKe3Gj_TK-sHvwb62e14ArugmK_FAhN7UqbX8hU9wP42LaWXqA7ps4kkJSx-sfgHqMzCKewlAZWwyZBoFgWEgoheKZ7ILkSGf0jzBZlS_1R0jFRSrlYD9rI1S4Px-HllS0t32wRCSbzkp6aVMRs46S0ePrN1mK3spsuQXtYhE2913ZC7p2KwyTGfC2FOOeJdRJknh6kI3Z7pTcsjN2jnQN3o8vPEkN3wl7MbAgAsHcUV45pvyxn4SNBmTMQ",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMCwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.3NjgS14SGFyJ6cix2XJZFPlcyeSu4LSduEMUIH0grJuCljbhalyoib5s4JnBaK4slKrQv1WHlhnKB737hX1FF7_EwQM3toCf--DBjrIuq5cYK3rzcn71JDe_op3CvClwpVyxd2vQZtQfP_tWqN6cNTuWF8ZQ0rJGug6Zb-NeE5h68YK_9tXLZC_i5anyjjAVONOc3Nd-TeIUBaLQKQXOddw0gcTcA7vg3uS0gXTEDq-_ZkF-v9bn1ua4_lgRPbuaYvrBFbXSCEdvNORPfPz4zfL3XU09q0gmnmXC9nxjUFVX4BjkP_YiCCO42sqUKY4y7STTB_IkK_04e2wntonVZA",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.b4pdohov81oqzLyCIp4y7e4VYz7LSez7bH0t1o0Zwzau1uXPYXcasT9lxxNMEEiZwHIovPLyWQ6XvF0bMWTk9vc4PyIpkLqsLBJPsuQ-wYUOD04fECmqUX_JaINqm2pPbohTcOQwl0xsE1UMIKTFBZDL1hEXGEMdW9lrPcXilhbC1ikyMpzsmVh55Q_wL2GqydssnOOcDQTqEkWoKvELJJhBcE-YuQkUp8jEVhF3VZ4jEZkzCErTlyXcfe1qXZHkWtw2QNo9s_SfLuRy_fACOo8XE9pHBoE7rqiSm-FmISgiLO1Jj3Pqq-abjN4SnAbU7PZWcV3fUoO1eYLGORmAcw",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDB9.yDGMBeee4hj8yDtEvVtIsS4tnkPjDMQADTkNh74wtb3oYPgQNqMRWKngXiwjvW2FmnsCUue2cFzLgTbpqlDq0QKcBP0i_UwBiXk9m2wLo0WRFtgw2zNHYSsowu26sFoEjKLgpPZzKrPlU4pnxqa8u3yqg8vIcSTlpX8t3uDqNqhUKP6x-w6wb25h67XDmnORiMwhaOZE_Gs9-H6uWnKdguTIlU1Tj4CjUEnZgZN7dJORiDnO_vHiAyL5yvRjhp5YK0Pq-TtCj5kWoJsjQiKc4laIcgofAKoq_b62Psns8MhxzAxwM7i0rbQZXXYB0VKMUho88uHlpbSWCZxu415lWw",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiZXhwIjo5NDY2ODQ4MDB9.BHSCjFeXS6B7KFJi1LpQMEd3ib4Bp9FY3WcB-v7dtP3Ay0SxQZz_gxIbi-tYiNCBQIlfKcfq6vELOjE1WJ5zxPDQM8uV0Pjl41hqYBu3qFv4649a-o2Cd-MaSPUSUogPxzTh2Bk4IdM3sG1Zbd_At4DR_DQwWJDuChA8duA5yG2XPkZr0YF1ZJ326O_jEowvCJiZpzOpH9QsLVPbiX49jtWTwqQGhvpKEj3ztTLFo8VHO-p8bhOGEph2F73F6-GB0XqiWk2Dm1yKAunJCMsM4qXooWfaX6gj-WFhPI9kEXNFfGmPal5i1gb17YoeinbdV2kjN42oxast2Iaa3CMldw",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDAsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.s6sElpfKL8WHWfbD_Kbwiy_ip4O082V8ElZqwugvDpS-7yQ3FTvQ3WXqtVAJc-fBZe4ZsBnrXUWwZV0Nhoe6iWKjEjTPjonQWbWL_WUJmIC2HVz18AOISnqReV2rcuLSHQ2ckhsyktlE9K1Rfj-Hi6f3HzzzePEgTsL2ZdBH6GrcmJVDFKqLLrkvOHShoPp7rcwuFBr0J_S1oqYac5O0B-u0OVnxBXTwij0ThrTGMgVCp2rn6Hk0NvtF6CE49Eu4XP8Ue-APT8l5_SjqX9GcrjkJp8Gif_oyBheL-zRg_v-cU60X6qY9wVolO8WodVPSnlE02XyYhLVxvfK-w5129A",
            ),
        )

    def test_decode_with_no_expiry(self):
        for backend in self.backends:
            with self.subTest("Test decode with no expiry for f{backend.algorithm}"):
                no_exp_token = jwt.encode(
                    self.payload, backend.signing_key, algorithm=backend.algorithm
                )

                backend.decode(no_exp_token)

    def test_decode_with_no_expiry_no_verify(self):
        for backend in self.backends:
            with self.subTest(
                "Test decode with no expiry and no verify for f{backend.algorithm}"
            ):
                no_exp_token = jwt.encode(
                    self.payload, backend.signing_key, algorithm=backend.algorithm
                )

                self.assertEqual(
                    backend.decode(no_exp_token, verify=False),
                    self.payload,
                )

    def test_decode_with_expiry(self):
        self.payload["exp"] = aware_utcnow() - timedelta(seconds=1)
        for backend in self.backends:
            with self.subTest("Test decode with expiry for f{backend.algorithm}"):

                expired_token = jwt.encode(
                    self.payload, backend.signing_key, algorithm=backend.algorithm
                )

                with self.assertRaises(TokenBackendError):
                    backend.decode(expired_token)

    def test_decode_with_invalid_sig(self):
        self.payload["exp"] = aware_utcnow() - timedelta(seconds=1)
        for backend in self.backends:
            with self.subTest(f"Test decode with invalid sig for {backend.algorithm}"):
                payload = self.payload.copy()
                payload["exp"] = aware_utcnow() + timedelta(days=1)
                token_1 = jwt.encode(
                    payload, backend.signing_key, algorithm=backend.algorithm
                )
                payload["foo"] = "baz"
                token_2 = jwt.encode(
                    payload, backend.signing_key, algorithm=backend.algorithm
                )

                if IS_OLD_JWT:
                    token_1 = token_1.decode("utf-8")
                    token_2 = token_2.decode("utf-8")

                token_2_payload = token_2.rsplit(".", 1)[0]
                token_1_sig = token_1.rsplit(".", 1)[-1]
                invalid_token = token_2_payload + "." + token_1_sig

                with self.assertRaises(TokenBackendError):
                    backend.decode(invalid_token)

    def test_decode_with_invalid_sig_no_verify(self):
        self.payload["exp"] = aware_utcnow() + timedelta(days=1)
        for backend in self.backends:
            with self.subTest("Test decode with invalid sig for f{backend.algorithm}"):
                payload = self.payload.copy()
                token_1 = jwt.encode(
                    payload, backend.signing_key, algorithm=backend.algorithm
                )
                payload["foo"] = "baz"
                token_2 = jwt.encode(
                    payload, backend.signing_key, algorithm=backend.algorithm
                )
                if IS_OLD_JWT:
                    token_1 = token_1.decode("utf-8")
                    token_2 = token_2.decode("utf-8")
                else:
                    # Payload copied
                    payload["exp"] = datetime_to_epoch(payload["exp"])

                token_2_payload = token_2.rsplit(".", 1)[0]
                token_1_sig = token_1.rsplit(".", 1)[-1]
                invalid_token = token_2_payload + "." + token_1_sig

                self.assertEqual(
                    backend.decode(invalid_token, verify=False),
                    payload,
                )

    def test_decode_success(self):
        self.payload["exp"] = aware_utcnow() + timedelta(days=1)
        self.payload["foo"] = "baz"
        for backend in self.backends:
            with self.subTest("Test decode success for f{backend.algorithm}"):

                token = jwt.encode(
                    self.payload, backend.signing_key, algorithm=backend.algorithm
                )
                if IS_OLD_JWT:
                    token = token.decode("utf-8")
                    payload = self.payload
                else:
                    # Payload copied
                    payload = self.payload.copy()
                    payload["exp"] = datetime_to_epoch(self.payload["exp"])

                self.assertEqual(backend.decode(token), payload)

    def test_decode_aud_iss_success(self):
        self.payload["exp"] = aware_utcnow() + timedelta(days=1)
        self.payload["foo"] = "baz"
        self.payload["aud"] = AUDIENCE
        self.payload["iss"] = ISSUER

        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm="RS256")
        if IS_OLD_JWT:
            token = token.decode("utf-8")
        else:
            # Payload copied
            self.payload["exp"] = datetime_to_epoch(self.payload["exp"])

        self.assertEqual(self.aud_iss_token_backend.decode(token), self.payload)

    @pytest.mark.skipif(
        not JWK_CLIENT_AVAILABLE,
        reason="PyJWT 1.7.1 doesn't have JWK client",
    )
    def test_decode_rsa_aud_iss_jwk_success(self):
        self.payload["exp"] = aware_utcnow() + timedelta(days=1)
        self.payload["foo"] = "baz"
        self.payload["aud"] = AUDIENCE
        self.payload["iss"] = ISSUER

        token = jwt.encode(
            self.payload,
            PRIVATE_KEY_2,
            algorithm="RS256",
            headers={"kid": "230498151c214b788dd97f22b85410a5"},
        )
        # Payload copied
        self.payload["exp"] = datetime_to_epoch(self.payload["exp"])

        mock_jwk_module = mock.MagicMock()
        with patch("rest_framework_simplejwt.backends.PyJWKClient") as mock_jwk_module:
            mock_jwk_client = mock.MagicMock()
            mock_signing_key = mock.MagicMock()

            mock_jwk_module.return_value = mock_jwk_client
            mock_jwk_client.get_signing_key_from_jwt.return_value = mock_signing_key
            type(mock_signing_key).key = mock.PropertyMock(return_value=PUBLIC_KEY_2)

            # Note the PRIV,PUB care is intentially the original pairing
            jwk_token_backend = TokenBackend(
                "RS256", PRIVATE_KEY, PUBLIC_KEY, AUDIENCE, ISSUER, JWK_URL
            )

            self.assertEqual(jwk_token_backend.decode(token), self.payload)

    def test_decode_when_algorithm_not_available(self):
        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm="RS256")
        if IS_OLD_JWT:
            token = token.decode("utf-8")

        pyjwt_without_rsa = PyJWS()
        pyjwt_without_rsa.unregister_algorithm("RS256")

        def _decode(jwt, key, algorithms, options, audience, issuer, leeway):
            return pyjwt_without_rsa.decode(jwt, key, algorithms, options)

        with patch.object(jwt, "decode", new=_decode):
            with self.assertRaisesRegex(
                TokenBackendError, "Invalid algorithm specified"
            ):
                self.rsa_token_backend.decode(token)

    def test_decode_when_token_algorithm_does_not_match(self):
        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm="RS256")
        if IS_OLD_JWT:
            token = token.decode("utf-8")

        with self.assertRaisesRegex(TokenBackendError, "Invalid algorithm specified"):
            self.hmac_token_backend.decode(token)

    def test_decode_leeway_hmac_fail(self):
        self.payload["exp"] = datetime_to_epoch(
            aware_utcnow() - timedelta(seconds=LEEWAY * 2)
        )

        expired_token = jwt.encode(self.payload, SECRET, algorithm="HS256")

        with self.assertRaises(TokenBackendError):
            self.hmac_leeway_token_backend.decode(expired_token)

    def test_decode_leeway_hmac_success(self):
        self.payload["exp"] = datetime_to_epoch(
            aware_utcnow() - timedelta(seconds=LEEWAY / 2)
        )

        expired_token = jwt.encode(self.payload, SECRET, algorithm="HS256")

        self.assertEqual(
            self.hmac_leeway_token_backend.decode(expired_token),
            self.payload,
        )

    def test_custom_JSONEncoder(self):
        backend = TokenBackend("HS256", SECRET, json_encoder=UUIDJSONEncoder)
        unique = uuid.uuid4()
        self.payload["uuid"] = unique
        token = backend.encode(self.payload)
        decoded = backend.decode(token)
        self.assertEqual(decoded["uuid"], str(unique))
