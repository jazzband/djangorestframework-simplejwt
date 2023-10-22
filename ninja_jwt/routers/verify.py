from ninja import Schema
from ninja.router import Router

from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings

schema = SchemaControl(api_settings)

verify_router = Router()


@verify_router.post(
    "/verify",
    response={200: Schema},
    url_name="token_verify",
    auth=None,
)
def verify_token(request, token: schema.verify_schema):
    return token.to_response_schema()
