from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
from django.test import TestCase
from jwt import PyJWS, algorithms

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.utils import (
    aware_utcnow, datetime_to_epoch, make_utc,
)

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

    @patch.object(algorithms, 'has_crypto', new=False)
    def test_init_fails_for_rs_algorithms_when_crypto_not_installed(self):
        with self.assertRaisesRegex(TokenBackendError, 'You must have cryptography installed to use RS256.'):
            TokenBackend('RS256', 'not_secret')
        with self.assertRaisesRegex(TokenBackendError, 'You must have cryptography installed to use RS384.'):
            TokenBackend('RS384', 'not_secret')
        with self.assertRaisesRegex(TokenBackendError, 'You must have cryptography installed to use RS512.'):
            TokenBackend('RS512', 'not_secret')

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
        original_payload = {'exp': make_utc(datetime(year=2000, month=1, day=1))}
        payload = original_payload.copy()

        rsa_token = self.aud_iss_token_backend.encode(payload)

        # Assert that payload has not been mutated by the encode() function
        self.assertEqual(payload, original_payload)

        # Token could be one of 12 depending on header dict ordering
        self.assertIn(
            rsa_token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCIsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.kSz7KyUZgpKaeQHYSQlhsE-UFLG2zhBiJ2MFCIvhstA4lSIKj3U1fdP1OhEDg7X66EquRRIZrby6M7RncqCdsjRwKrEIaL74KgC4s5PDXa_HC6dtpi2GhXqaLz8YxfCPaNGZ_9q9rs4Z4O6WpwBLNmMQrTxNno9p0uT93Z2yKj5hGih8a9C_CSf_rKtsHW9AJShWGoKpR6qQFKVNP1GAwQOQ6IeEvZenq_LSEywnrfiWp4Y5UF7xi42wWx7_YPQtM9_Bp5sB-DbrKg_8t0zSc-OHeVDgH0TKqygGEea09W0QkmJcROkaEbxt2LxJg9OuSdXgudVytV8ewpgNtWNE4g',
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMCwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.l-sJR5VKGKNrEn5W8sfO4tEpPq4oQ-Fm5ttQyqUkF6FRJHmCfS1TZIUSXieDLHmarnb4hdIGLr5y-EAbykiqYaTn8d25oT2_zIPlCYHt0DxxeuOliGad5l3AXbWee0qPoZL7YCV8FaSdv2EjtMDOEiJBG5yTkaqZlRmSkbfqu1_y2DRErv3X5LpfEHuKoum4jv5YpoCS6wAWDaWJ9cXMPQaGc4gXg4cuSQxb_EjiQ3QYyztHhG37gOu1J-r_rudaiiIk_VZQdYNfCcirp8isS0z2dcNij_0bELp_oOaipsF7uwzc6WfNGR7xP50X1a_K6EBZzVs0eXFxvl9b3C_d8A',
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDAsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.aTwQEIxSzhI5fN4ffQMzZ6h61Ur-Gzh_gPkgOyyWvMX890Z18tC2RisEjXeL5xDGKe2XiEAVtuJa9CjXB9eJoCxNN1k05C-ph82cco-0m_TbMbs0d1MFnfC9ESr4JKynP_Klxi8bi0iZMazduT15pH4UhRkEGsnp8rOKtlt_8_8UOGBJAzG34161lM4JbZqrZDit1DvQdGxaC0lmMgosKg3NDMECfkPe3pGLJ5F_su5yhQk0xyKNCjYyE2FNlilWoDV2KkGiCWdsFOgRMAJwHZ-cdgPg8Vyh2WthBNblsbRVfDrGtfPX0VuW5B0RhBhvI5Iut34P9kkxKRFo3NaiEg',
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiZXhwIjo5NDY2ODQ4MDB9.w46s7u28LgsnmK6K_5O15q1SFkKeRgkkplFLi5idq1z7qJjXUi45qpXIyQw3W8a0k1fwa22WB_0XC1MTo22OK3Z0aGNCI2ZCBxvZGOAc1WcCUae44a9LckPHp80q0Hs03NvjsuRVLGXRwDVHrYxuGnFxQSEMbZ650-MQkfVFIXVzMOOAn5Yl4ntjigLcw8iPEqJPnDLdFUSnObZjRzK1M6mJf0-125pqcFsCJaa49rjdbTtnN-VuGnKmv9wV1GwevRQPWjx2vinETURVO9IyZCDtdaLJkvL7Z5IpToK5jrZPc1UWAR0VR8WeWfussFoHzJF86LxVxnqIeXnqOhq5SQ',
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDB9.Np_SJYye14vz0cvALvfYNqZXvXMD_gY6kIaxA458kbeu6veC_Ds45uWgjJFhTSYFAFWd3TB6M7qZbWgiO0ycION2-B9Yfgaf82WzNtPfgDhu51w1cbLnvuOSRvgX69Q6Z2i1SByewKaSDw25BaMv9Ty4DBdoCbG62qELnNKjDSQvuHlz8cRJv2I6xJBeOYgZV-YN8Zmxsles44a57Vvcj-DjVouHj5m4LperIxb9islNUQBPRTbvw1d_tR8O8ny0mQqbsWL7e2J-wfwdduVf1kVCPePkhHMM6GLhPIrSoTgMzZuRYLBJ61yphuDK98zTknNBM-Jtn5cMyBwP9JBJvA',
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.KJcWZtEluPrkRbYj2i_QmdWpZqGZt63Q8nO4QAJ4B4418ZfmgB6A54_vUmWd3Xc18DYgReLoNPlaOuRXtR7rzlMk0-ADjV0bsca5NwTNAV2F-gR9Xsr9iFlcPMNAYf4CAs85gg7deMIxlbGTAaoft__58ah2_vdd8o_nem1PdzsPC198AYtcwnIV206qpeCNR8S_ZTU46OaHwCoySVRx9E7tNG13YSCmGvBaEqgQHKH82qLXo0KivFrjGmGP0xePFG1B8HCZl-LH1euXGGCp6S48q-tmepX5GJwvzaZNBam4pfxQ0GIHa7z11e7sEN-196iDPCK8NzDcXFwHOAnyaA',
                'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCIsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.MfhVcFN-9Rd0j11CLtxopzREKdyJH1loSpD4ibjP6Aco4-iM5C99B6gliPgOldtuevhneXV2I7NGhmZFULaYhulcLrAgKe3Gj_TK-sHvwb62e14ArugmK_FAhN7UqbX8hU9wP42LaWXqA7ps4kkJSx-sfgHqMzCKewlAZWwyZBoFgWEgoheKZ7ILkSGf0jzBZlS_1R0jFRSrlYD9rI1S4Px-HllS0t32wRCSbzkp6aVMRs46S0ePrN1mK3spsuQXtYhE2913ZC7p2KwyTGfC2FOOeJdRJknh6kI3Z7pTcsjN2jnQN3o8vPEkN3wl7MbAgAsHcUV45pvyxn4SNBmTMQ',
                'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMCwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.3NjgS14SGFyJ6cix2XJZFPlcyeSu4LSduEMUIH0grJuCljbhalyoib5s4JnBaK4slKrQv1WHlhnKB737hX1FF7_EwQM3toCf--DBjrIuq5cYK3rzcn71JDe_op3CvClwpVyxd2vQZtQfP_tWqN6cNTuWF8ZQ0rJGug6Zb-NeE5h68YK_9tXLZC_i5anyjjAVONOc3Nd-TeIUBaLQKQXOddw0gcTcA7vg3uS0gXTEDq-_ZkF-v9bn1ua4_lgRPbuaYvrBFbXSCEdvNORPfPz4zfL3XU09q0gmnmXC9nxjUFVX4BjkP_YiCCO42sqUKY4y7STTB_IkK_04e2wntonVZA',
                'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJleHAiOjk0NjY4NDgwMCwiYXVkIjoib3BlbmlkLWNsaWVudC1pZCJ9.b4pdohov81oqzLyCIp4y7e4VYz7LSez7bH0t1o0Zwzau1uXPYXcasT9lxxNMEEiZwHIovPLyWQ6XvF0bMWTk9vc4PyIpkLqsLBJPsuQ-wYUOD04fECmqUX_JaINqm2pPbohTcOQwl0xsE1UMIKTFBZDL1hEXGEMdW9lrPcXilhbC1ikyMpzsmVh55Q_wL2GqydssnOOcDQTqEkWoKvELJJhBcE-YuQkUp8jEVhF3VZ4jEZkzCErTlyXcfe1qXZHkWtw2QNo9s_SfLuRy_fACOo8XE9pHBoE7rqiSm-FmISgiLO1Jj3Pqq-abjN4SnAbU7PZWcV3fUoO1eYLGORmAcw',
                'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3d3dy5teW9pZGNwcm92aWRlci5jb20iLCJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDB9.yDGMBeee4hj8yDtEvVtIsS4tnkPjDMQADTkNh74wtb3oYPgQNqMRWKngXiwjvW2FmnsCUue2cFzLgTbpqlDq0QKcBP0i_UwBiXk9m2wLo0WRFtgw2zNHYSsowu26sFoEjKLgpPZzKrPlU4pnxqa8u3yqg8vIcSTlpX8t3uDqNqhUKP6x-w6wb25h67XDmnORiMwhaOZE_Gs9-H6uWnKdguTIlU1Tj4CjUEnZgZN7dJORiDnO_vHiAyL5yvRjhp5YK0Pq-TtCj5kWoJsjQiKc4laIcgofAKoq_b62Psns8MhxzAxwM7i0rbQZXXYB0VKMUho88uHlpbSWCZxu415lWw',
                'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiaXNzIjoiaHR0cHM6Ly93d3cubXlvaWRjcHJvdmlkZXIuY29tIiwiZXhwIjo5NDY2ODQ4MDB9.BHSCjFeXS6B7KFJi1LpQMEd3ib4Bp9FY3WcB-v7dtP3Ay0SxQZz_gxIbi-tYiNCBQIlfKcfq6vELOjE1WJ5zxPDQM8uV0Pjl41hqYBu3qFv4649a-o2Cd-MaSPUSUogPxzTh2Bk4IdM3sG1Zbd_At4DR_DQwWJDuChA8duA5yG2XPkZr0YF1ZJ326O_jEowvCJiZpzOpH9QsLVPbiX49jtWTwqQGhvpKEj3ztTLFo8VHO-p8bhOGEph2F73F6-GB0XqiWk2Dm1yKAunJCMsM4qXooWfaX6gj-WFhPI9kEXNFfGmPal5i1gb17YoeinbdV2kjN42oxast2Iaa3CMldw',
                'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJvcGVuaWQtY2xpZW50LWlkIiwiZXhwIjo5NDY2ODQ4MDAsImlzcyI6Imh0dHBzOi8vd3d3Lm15b2lkY3Byb3ZpZGVyLmNvbSJ9.s6sElpfKL8WHWfbD_Kbwiy_ip4O082V8ElZqwugvDpS-7yQ3FTvQ3WXqtVAJc-fBZe4ZsBnrXUWwZV0Nhoe6iWKjEjTPjonQWbWL_WUJmIC2HVz18AOISnqReV2rcuLSHQ2ckhsyktlE9K1Rfj-Hi6f3HzzzePEgTsL2ZdBH6GrcmJVDFKqLLrkvOHShoPp7rcwuFBr0J_S1oqYac5O0B-u0OVnxBXTwij0ThrTGMgVCp2rn6Hk0NvtF6CE49Eu4XP8Ue-APT8l5_SjqX9GcrjkJp8Gif_oyBheL-zRg_v-cU60X6qY9wVolO8WodVPSnlE02XyYhLVxvfK-w5129A',
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
        token_1 = jwt.encode(self.payload, SECRET, algorithm='HS256')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, SECRET, algorithm='HS256')

        token_2_payload = token_2.rsplit('.', 1)[0]
        token_1_sig = token_1.rsplit('.', 1)[-1]
        invalid_token = token_2_payload + '.' + token_1_sig

        with self.assertRaises(TokenBackendError):
            self.hmac_token_backend.decode(invalid_token)

    def test_decode_hmac_with_invalid_sig_no_verify(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(self.payload, SECRET, algorithm='HS256')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, SECRET, algorithm='HS256')
        # Payload copied
        self.payload["exp"] = datetime_to_epoch(self.payload["exp"])

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

        token = jwt.encode(self.payload, SECRET, algorithm='HS256')
        # Payload copied
        self.payload["exp"] = datetime_to_epoch(self.payload["exp"])

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
        token_1 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')

        token_2_payload = token_2.rsplit('.', 1)[0]
        token_1_sig = token_1.rsplit('.', 1)[-1]
        invalid_token = token_2_payload + '.' + token_1_sig

        with self.assertRaises(TokenBackendError):
            self.rsa_token_backend.decode(invalid_token)

    def test_decode_rsa_with_invalid_sig_no_verify(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        token_1 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')
        self.payload['foo'] = 'baz'
        token_2 = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')

        token_2_payload = token_2.rsplit('.', 1)[0]
        token_1_sig = token_1.rsplit('.', 1)[-1]
        invalid_token = token_2_payload + '.' + token_1_sig
        # Payload copied
        self.payload["exp"] = datetime_to_epoch(self.payload["exp"])

        self.assertEqual(
            self.hmac_token_backend.decode(invalid_token, verify=False),
            self.payload,
        )

    def test_decode_rsa_success(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        self.payload['foo'] = 'baz'

        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')
        # Payload copied
        self.payload["exp"] = datetime_to_epoch(self.payload["exp"])

        self.assertEqual(self.rsa_token_backend.decode(token), self.payload)

    def test_decode_aud_iss_success(self):
        self.payload['exp'] = aware_utcnow() + timedelta(days=1)
        self.payload['foo'] = 'baz'
        self.payload['aud'] = AUDIENCE
        self.payload['iss'] = ISSUER

        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')
        # Payload copied
        self.payload["exp"] = datetime_to_epoch(self.payload["exp"])

        self.assertEqual(self.aud_iss_token_backend.decode(token), self.payload)

    def test_decode_when_algorithm_not_available(self):
        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')

        pyjwt_without_rsa = PyJWS()
        pyjwt_without_rsa.unregister_algorithm('RS256')
        with patch.object(jwt, 'decode', new=pyjwt_without_rsa.decode):
            with self.assertRaisesRegex(TokenBackendError, 'Invalid algorithm specified'):
                self.rsa_token_backend.decode(token)

    def test_decode_when_token_algorithm_does_not_match(self):
        token = jwt.encode(self.payload, PRIVATE_KEY, algorithm='RS256')

        with self.assertRaisesRegex(TokenBackendError, 'Invalid algorithm specified'):
            self.hmac_token_backend.decode(token)
