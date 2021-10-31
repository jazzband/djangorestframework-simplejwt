import pytest
from django.contrib.auth import get_user_model
from ninja_extra import NinjaExtraAPI

from ninja_jwt.controller import SimpleJWTDefaultController
from ninja_jwt.schema import TokenObtainPairSerializer, TokenObtainSerializer

# api = NinjaExtraAPI()
# api.register_controllers(SimpleJWTDefaultController)


@pytest.mark.django_db
class TestSchemas:
    def test_tokenObtainSerializer(self):
        api = NinjaExtraAPI()
        api.register_controllers(SimpleJWTDefaultController)
        # UserModel = get_user_model()
        # UserModel.objects.create_user(username='Emeka', password='password')
        # schema = TokenObtainSerializer(username='Emeka', password='password')
        # print(schema.json())
        # schema = TokenObtainPairSerializer(username='Emeka', password='password')
        # print(schema.json())
        # assert schema.dict()
