import pytest
from django.contrib.auth import get_user_model
from ninja import NinjaAPI
from ninja_extra import exceptions
from ninja_extra.testing import TestClient

from ninja_jwt.routers.blacklist import blacklist_router
from ninja_jwt.routers.obtain import obtain_pair_router, sliding_router
from ninja_jwt.routers.verify import verify_router
from ninja_jwt.tokens import RefreshToken, SlidingToken

api = NinjaAPI()
client = TestClient(api)


def api_exception_handler(request, exc):
    headers = {}

    if isinstance(exc.detail, (list, dict)):
        data = exc.detail
    else:
        data = {"detail": exc.detail}

    response = api.create_response(request, data, status=exc.status_code)
    for k, v in headers.items():
        response.setdefault(k, v)

    return response


api.exception_handler(exceptions.APIException)(api_exception_handler)
api.add_router("", obtain_pair_router)
api.add_router("", sliding_router)
api.add_router("", verify_router)
api.add_router("", blacklist_router)

User = get_user_model()


@pytest.mark.django_db
class TestObtainTokenRouter:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"
        self.user = User.objects.create(
            email="test@user.com",
            username="test_user",
            password="test_password",
            is_active=True,
        )
        self.user.set_password(self.password)
        self.user.save()

    def test_obtain_tokek_pair_success(self):
        response = client.post(
            "/pair",
            json={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert response.status_code == 200

        assert "access" in response.json()
        assert "refresh" in response.json()
        assert User.USERNAME_FIELD in response.json()

    def test_obtain_tokek_pair_fail(self):
        response = client.post(
            "/pair",
            json={
                User.USERNAME_FIELD: self.username,
                "password": "wrong_password",
            },
            content_type="application/json",
        )
        assert response.status_code == 401

        assert "detail" in response.json()
        assert "code" in response.json()

    def test_obtain_tokek_pair_fail_user_not_active(self):
        self.user.is_active = False
        self.user.save()

        response = client.post(
            "/pair",
            json={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert response.status_code == 401

        assert "detail" in response.json()
        assert "code" in response.json()

    def test_refresh_token_success(self):
        token = RefreshToken.for_user(self.user)

        response = client.post(
            "/refresh",
            json={
                "refresh": str(token),
            },
            content_type="application/json",
        )
        assert response.status_code == 200

        assert "access" in response.json()
        assert "refresh" in response.json()

    def test_refresh_token_fail(self):
        response = client.post(
            "/refresh",
            json={
                "refresh": "wrong_refresh_token",
            },
            content_type="application/json",
        )
        assert response.status_code == 401

        assert "detail" in response.json()
        assert "code" in response.json()

    def test_obtain_token_sliding_success(self):
        response = client.post(
            "/sliding",
            json={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert response.status_code == 200

        assert "token" in response.json()
        assert User.USERNAME_FIELD in response.json()

    def test_obtain_token_sliding_fail(self):
        response = client.post(
            "/sliding",
            json={
                User.USERNAME_FIELD: self.username,
                "password": "wrong_password",
            },
            content_type="application/json",
        )
        assert response.status_code == 401

        assert "detail" in response.json()
        assert "code" in response.json()

    def test_obtain_token_sliding_fail_user_not_active(self):
        self.user.is_active = False
        self.user.save()

        response = client.post(
            "/sliding",
            json={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert response.status_code == 401

        assert "detail" in response.json()
        assert "code" in response.json()

    def test_refresh_sliding_token_success(self):
        token = SlidingToken.for_user(self.user)

        response = client.post(
            "/sliding/refresh",
            json={"token": str(token)},
            content_type="application/json",
        )
        assert response.status_code == 200

        assert "token" in response.json()

    def test_refresh_sliding_token_token_fail(self):
        token = SlidingToken.for_user(self.user)
        response = client.post(
            "/refresh",
            json={"refresh": str(token)},
            content_type="application/json",
        )
        assert response.status_code == 401

        assert "detail" in response.json()
        assert "code" in response.json()

    def test_verify_token_success(self):
        token = RefreshToken.for_user(self.user)
        response = client.post(
            "/verify",
            json={
                "token": str(token),
            },
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_verify_token_fail(self):
        response = client.post(
            "/verify",
            json={
                "token": "wrong_token",
            },
            content_type="application/json",
        )
        assert response.status_code == 401

        assert "detail" in response.json()
        assert "code" in response.json()

    def test_blacklist_token_success(self):
        token = RefreshToken.for_user(self.user)
        response = client.post(
            "/blacklist",
            json={
                "refresh": str(token),
            },
            content_type="application/json",
        )
        assert response.status_code == 200
