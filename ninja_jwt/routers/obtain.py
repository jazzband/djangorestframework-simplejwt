from ninja.router import Router

from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings

schema = SchemaControl(api_settings)

obtain_pair_router = Router()
sliding_router = Router()


@obtain_pair_router.post(
    "/pair",
    response=schema.obtain_pair_schema.get_response_schema(),
    url_name="token_obtain_pair",
    auth=None,
)
def obtain_token(request, user_token: schema.obtain_pair_schema):
    user_token.check_user_authentication_rule()
    return user_token.output_schema()


@obtain_pair_router.post(
    "/refresh",
    response=schema.obtain_pair_refresh_schema.get_response_schema(),
    url_name="token_refresh",
    auth=None,
)
def refresh_token(request, refresh_token: schema.obtain_pair_refresh_schema):
    return refresh_token.to_response_schema()


@sliding_router.post(
    "/sliding",
    response=schema.obtain_sliding_schema.get_response_schema(),
    url_name="token_obtain_sliding",
    auth=None,
)
def obtain_token_sliding_token(request, user_token: schema.obtain_sliding_schema):
    user_token.check_user_authentication_rule()
    return user_token.to_response_schema()


@sliding_router.post(
    "/sliding/refresh",
    response=schema.obtain_sliding_refresh_schema.get_response_schema(),
    url_name="token_refresh_sliding",
    auth=None,
)
def refresh_token_sliding(request, refresh_token: schema.obtain_sliding_refresh_schema):
    return refresh_token.to_response_schema()
