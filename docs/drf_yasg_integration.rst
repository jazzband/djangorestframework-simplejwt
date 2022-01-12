.. _drf_yasg_integration

``drf-yasg`` Integration
------------------------

`drf-yasg`_ is a library that automatically generates an OpenAPI schema by
inspecting DRF ``Serializer`` definitions. Because
``django-rest-framework-simplejwt`` serializers are not symmetric, if you
want to generate correct OpenAPI schemas for your JWT token endpoints, use the
following code to decorate your JWT ``View`` definitions.

.. code-block:: python

    from drf_yasg.utils import swagger_auto_schema
    from rest_framework import serializers, status
    from rest_framework_simplejwt.views import (
        TokenBlacklistView,
        TokenObtainPairView,
        TokenRefreshView,
        TokenVerifyView,
    )


    class TokenObtainPairResponseSerializer(serializers.Serializer):
        access = serializers.CharField()
        refresh = serializers.CharField()

        def create(self, validated_data):
            raise NotImplementedError()

        def update(self, instance, validated_data):
            raise NotImplementedError()


    class DecoratedTokenObtainPairView(TokenObtainPairView):
        @swagger_auto_schema(
            responses={
                status.HTTP_200_OK: TokenObtainPairResponseSerializer,
            }
        )
        def post(self, request, *args, **kwargs):
            return super().post(request, *args, **kwargs)


    class TokenRefreshResponseSerializer(serializers.Serializer):
        access = serializers.CharField()

        def create(self, validated_data):
            raise NotImplementedError()

        def update(self, instance, validated_data):
            raise NotImplementedError()


    class DecoratedTokenRefreshView(TokenRefreshView):
        @swagger_auto_schema(
            responses={
                status.HTTP_200_OK: TokenRefreshResponseSerializer,
            }
        )
        def post(self, request, *args, **kwargs):
            return super().post(request, *args, **kwargs)


    class TokenVerifyResponseSerializer(serializers.Serializer):
        def create(self, validated_data):
            raise NotImplementedError()

        def update(self, instance, validated_data):
            raise NotImplementedError()


    class DecoratedTokenVerifyView(TokenVerifyView):
        @swagger_auto_schema(
            responses={
                status.HTTP_200_OK: TokenVerifyResponseSerializer,
            }
        )
        def post(self, request, *args, **kwargs):
            return super().post(request, *args, **kwargs)


    class TokenBlacklistResponseSerializer(serializers.Serializer):
        def create(self, validated_data):
            raise NotImplementedError()

        def update(self, instance, validated_data):
            raise NotImplementedError()


    class DecoratedTokenBlacklistView(TokenBlacklistView):
        @swagger_auto_schema(
            responses={
                status.HTTP_200_OK: TokenBlacklistResponseSerializer,
            }
        )   
        def post(self, request, *args, **kwargs):
            return super().post(request, *args, **kwargs)

.. _drf-yasg: https://github.com/axnsan12/drf-yasg
