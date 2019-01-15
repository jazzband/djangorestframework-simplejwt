from datetime import datetime, timedelta

import jwt
from django.test import TestCase

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.utils import aware_utcnow, make_utc

SECRET = 'not_secret'

PRIVATE_KEY = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA3xMJfyl8TOdrsjDLSIodsArJ/NnQB3ZdfbFC5onxATDfRLLA
CHFo3ye694doBKeSe1NFYbfXPvahl6ODX1a23oQyoRQwlL+M99cLcdCa0gGuJXdb
AaF6Em8E+7uSb3290mI+rZmjqyc7gMtKVWKL4e5i2PerFFBoYkZ7E90KOp2t0ZAD
x2uqF4VTOfYLHG0cPgSw9/ptDStJqJVAOiRRqbv0j0GOFMDYNcN0mDlnpryhQFbQ
iMqn4IJIURZUVBJujFSa45cJPvSmMb6NrzZ1crg5UN6/5Mu2mxQzAi21+vpgGL+E
EuekUd7sRgEAjTHjLKzotLAGo7EGa8sL1vMSFwIDAQABAoIBAQCGGWabF/BONswq
CWUazVR9cG7uXm3NHp2jIr1p40CLC7scDCyeprZ5d+PQS4j/S1Ema++Ih8CQbCjG
BJjD5lf2OhhJdt6hfOkcUBzkJZf8aOAsS6zctRqyHCUtwxuLhFZpM4AkUfjuuZ3u
lcawv5YBkpG/hltE0fV+Jop0bWtpwiKxVsHXVcS0WEPXic0lsOTBCw8m81JXqjir
PCBOnkxgNpHSt69S1xnW3l9fPUWVlduO3EIZ5PZG2BxU081eZW31yIlKsDJhfgm6
R5Vlr5DynqeojAd6SNliCzNXZP28GOpQBrYIeVQWA1yMANvkvd4apz9GmDrjF/Fd
g8Chah+5AoGBAPc/+zyuDZKVHK7MxwLPlchCm5Zb4eou4ycbwEB+P3gDS7MODGu4
qvx7cstTZMuMavNRcJsfoiMMrke9JrqGe4rFGiKRFLVBY2Xwr+95pKNC11EWI1lF
5qDAmreDsj2alVJT5yZ9hsAWTsk2i+xj+/XHWYVkr67pRvOPRAmGMB+NAoGBAOb4
CBHe184Hn6Ie+gSD4OjewyUVmr3JDJ41s8cjb1kBvDJ/wv9Rvo9yz2imMr2F0YGc
ytHraM77v8KOJuJWpvGjEg8I0a/rSttxWQ+J0oYJSIPn+eDpAijNWfOp1aKRNALT
pboCXcnSn+djJFKkNJ2hR7R/vrrM6Jyly1jcVS0zAoGAQpdt4Cr0pt0YS5AFraEh
Mz2VUArRLtSQA3F69yPJjlY85i3LdJvZGYVaJp8AT74y8/OkQ3NipNP+gH3WV3hu
/7IUVukCTcsdrVAE4pe9mucevM0cmie0dOlLAlArCmJ/Axxr7jbyuvuHHrRdPT60
lr6pQr8afh6AKIsWhQYqIeUCgYA+v9IJcN52hhGzjPDl+yJGggbIc3cn6pA4B2UB
TDo7F0KXAajrjrzT4iBBUS3l2Y5SxVNA9tDxsumlJNOhmGMgsOn+FapKPgWHWuMU
WqBMdAc0dvinRwakKS4wCcsVsJdN0UxsHap3Y3a3+XJr1VrKHIALpM0fmP31WQHG
8Y1eiwKBgF6AYXxo0FzZacAommZrAYoxFZT1u4/rE/uvJ2K9HYRxLOVKZe+89ki3
D7AOmrxe/CAc/D+nNrtUIv3RFGfadfSBWzyLw36ekW76xPdJgqJsSz5XJ/FgzDW+
WNC5oOtiPOMCymP75oKOjuZJZ2SPLRmiuO/qvI5uAzBHxRC1BKdt
-----END RSA PRIVATE KEY-----
'''

PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3xMJfyl8TOdrsjDLSIod
sArJ/NnQB3ZdfbFC5onxATDfRLLACHFo3ye694doBKeSe1NFYbfXPvahl6ODX1a2
3oQyoRQwlL+M99cLcdCa0gGuJXdbAaF6Em8E+7uSb3290mI+rZmjqyc7gMtKVWKL
4e5i2PerFFBoYkZ7E90KOp2t0ZADx2uqF4VTOfYLHG0cPgSw9/ptDStJqJVAOiRR
qbv0j0GOFMDYNcN0mDlnpryhQFbQiMqn4IJIURZUVBJujFSa45cJPvSmMb6NrzZ1
crg5UN6/5Mu2mxQzAi21+vpgGL+EEuekUd7sRgEAjTHjLKzotLAGo7EGa8sL1vMS
FwIDAQAB
-----END PUBLIC KEY-----
'''

AUDIENCE = 'openid-client-id'

ISSUER = 'https://www.myoidcprovider.com'


class TestTokenBackend(TestCase):
    def setUp(self):
        self.hmac_token_backend = TokenBackend('HS256', SECRET)
        self.rsa_token_backend = TokenBackend('RS256', PRIVATE_KEY, PUBLIC_KEY)
        self.aud_iss_token_backend = TokenBackend('RS256', PRIVATE_KEY, PUBLIC_KEY, AUDIENCE, ISSUER)
        self.payload = {'foo': 'bar'}

    def test_init(self):
        # Should reject unknown algorithms
        with self.assertRaises(TokenBackendError):
            TokenBackend('oienarst oieanrsto i', 'not_secret')

        TokenBackend('HS256', 'not_secret')

    def test_encode_hmac(self):
        # Should return a JSON web token for the given payload
        payload = {'exp': make_utc(datetime(year=2000, month=1, day=1))}

        hmac_token = self.hmac_token_backend.encode(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            hmac_token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.NHpdD2X8ub4SE_MZLBedWa57FCpntGaN_r6f8kNKdUs',
                'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.jvxQgXCSDToR8uKoRJcMT-LmMJJn2-NM76nfSR2FOgs',
            ),
        )

    def test_encode_rsa(self):
        # Should return a JSON web token for the given payload
        payload = {'exp': make_utc(datetime(year=2000, month=1, day=1))}

        rsa_token = self.rsa_token_backend.encode(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            rsa_token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.cuE6ocmdxVHXVrGufzn-_ZbXDV475TPPb5jtSacvJsnR3s3tLIm9yR7MF4vGcCAUGJn2hU_JgSOhs9sxntPPVjdwvC3-sxAwfUQ5AgUCEAF5XC7wTvGhmvufzhAgEG_DNsactCh79P8xRnc0iugtlGNyFp_YK582-ZrlfQEp-7C0L9BNG_JCS2J9DsGR7ojO2xGFkFfzezKRkrVTJMPLwpl0JAiZ0iqbQE-Tex7redCrGI388_mgh52GLsNlSIvW2gQMqCVMYndMuYx32Pd5tuToZmLUQ2PJ9RyAZ4fOMApTzoshItg4lGqtnt9CDYzypHULJZohJIPcxFVZZfHxhw',
                'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.pzHTOaVvKJMMkSqksGh-NdeEvQy8Thre3hBM3smUW5Sohtg77KnHpaUYjq30DyRmYQRmPSjEVprh1Yvic_-OeAXPW8WVsF-r4YdJuxWUpuZbIPwJ9E-cMfTZkDkOl18z1zOdlsLtsP2kXyAlptyy9QQsM7AxoqM6cyXoQ5TI0geWccgoahTy3cBtA6pmjm7H0nfeDGqpqYQBhtaFmRuIWn-_XtdN9C6NVmRCcZwyjH-rP3oEm6wtuKJEN25sVWlZm8YRQ-rj7A7SNqBB5tFK2anM_iv4rmBlIEkmr_f2s_WqMxn2EWUSNeqbqiwabR6CZUyJtKx1cPG0B2PqOTcZsg',
            ),
        )

    def test_encode_aud_iss(self):
        # Should return a JSON web token for the given payload
        payload = {'exp': make_utc(datetime(year=2000, month=1, day=1))}

        rsa_token = self.aud_iss_token_backend.encode(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            rsa_token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCIsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.kSz7KyUZgpKaeQHYSQlhsE-UFLG2zhBiJ2MFCIvhstA4lSIKj3U1fdP1OhEDg7X66EquRRIZrby6M7RncqCdsjRwKrEIaL74KgC4s5PDXa_HC6dtpi2GhXqaLz8YxfCPaNGZ_9q9rs4Z4O6WpwBLNmMQrTxNno9p0uT93Z2yKj5hGih8a9C_CSf_rKtsHW9AJShWGoKpR6qQFKVNP1GAwQOQ6IeEvZenq_LSEywnrfiWp4Y5UF7xi42wWx7_YPQtM9_Bp5sB-DbrKg_8t0zSc-OHeVDgH0TKqygGEea09W0QkmJcROkaEbxt2LxJg9OuSdXgudVytV8ewpgNtWNE4g'
            ),
        )

    def test_decode_hmac_with_no_expiry(self):
        no_exp_token = jwt.encode(self.payload, SECRET, algorithm='HS256')

        self.hmac_token_backend.decode(no_exp_token)

    def test_decode_hmac_with_no_expiry_no_verify(self):
        no_exp_token = jwt.encode(self.payload, SECRET, algorithm='HS256')

        self.assertEqual(
            self.hmac_token_backend.decode(no_exp_token, verify=False),
            self.payload,
        )

    def test_decode_hmac_with_expiry(self):
        self.payload['exp'] = aware_utcnow() - timedelta(seconds=1)

        expired_token = jwt.encode(self.payload, SECRET, algorithm='HS256')

        with self.assertRaises(TokenBackendError):
            self.hmac_token_backend.decode(expired_token)

    def test_decode_hmac_with_invalid_sig(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(self.payload, SECRET, algorithm='HS256').decode('utf-8')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, SECRET, algorithm='HS256').decode('utf-8')

        token_2_payload = token_2.rsplit('.', 1)[0]
        token_1_sig = token_1.rsplit('.', 1)[-1]
        invalid_token = token_2_payload + '.' + token_1_sig

        with self.assertRaises(TokenBackendError):
            self.hmac_token_backend.decode(invalid_token)

    def test_decode_hmac_with_invalid_sig_no_verify(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(self.payload, SECRET, algorithm='HS256').decode('utf-8')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, SECRET, algorithm='HS256').decode('utf-8')

        token_2_payload = token_2.rsplit('.', 1)[0]
        token_1_sig = token_1.rsplit('.', 1)[-1]
        invalid_token = token_2_payload + '.' + token_1_sig

        self.assertEqual(
            self.hmac_token_backend.decode(invalid_token, verify=False),
            self.payload,
        )

    def test_decode_hmac_success(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        self.payload['foo'] = 'baz'

        token = jwt.encode(self.payload, SECRET, algorithm='HS256').decode('utf-8')

        self.assertEqual(self.hmac_token_backend.decode(token), self.payload)

    def test_decode_rsa_with_no_expiry(self):
        no_exp_token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')

        self.rsa_token_backend.decode(no_exp_token)

    def test_decode_rsa_with_no_expiry_no_verify(self):
        no_exp_token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')

        self.assertEqual(
            self.hmac_token_backend.decode(no_exp_token, verify=False),
            self.payload,
        )

    def test_decode_rsa_with_expiry(self):
        self.payload['exp'] = aware_utcnow() - timedelta(seconds=1)

        expired_token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')

        with self.assertRaises(TokenBackendError):
            self.rsa_token_backend.decode(expired_token)

    def test_decode_rsa_with_invalid_sig(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256').decode('utf-8')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256').decode('utf-8')

        token_2_payload = token_2.rsplit('.', 1)[0]
        token_1_sig = token_1.rsplit('.', 1)[-1]
        invalid_token = token_2_payload + '.' + token_1_sig

        with self.assertRaises(TokenBackendError):
            self.rsa_token_backend.decode(invalid_token)

    def test_decode_rsa_with_invalid_sig_no_verify(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256').decode('utf-8')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256').decode('utf-8')

        token_2_payload = token_2.rsplit('.', 1)[0]
        token_1_sig = token_1.rsplit('.', 1)[-1]
        invalid_token = token_2_payload + '.' + token_1_sig

        self.assertEqual(
            self.hmac_token_backend.decode(invalid_token, verify=False),
            self.payload,
        )

    def test_decode_rsa_success(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        self.payload['foo'] = 'baz'

        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256').decode('utf-8')

        self.assertEqual(self.rsa_token_backend.decode(token), self.payload)

    def test_decode_aud_iss_success(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        self.payload['foo'] = 'baz'
        self.payload['aud'] = AUDIENCE
        self.payload['iss'] = ISSUER

        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256').decode('utf-8')

        self.assertEqual(self.aud_iss_token_backend.decode(token), self.payload)
