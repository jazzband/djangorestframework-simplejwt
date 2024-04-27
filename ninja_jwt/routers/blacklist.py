from ninja.router import Router

from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings

blacklist_router = Router()

schema = SchemaControl(api_settings)


@blacklist_router.post(
    "/blacklist",
    response={200: schema.blacklist_schema.get_response_schema()},
    url_name="token_blacklist",
    auth=None,
)
def blacklist_token(request, refresh: schema.blacklist_schema):
    return refresh.to_response_schema()
