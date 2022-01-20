import django
from ninja_extra import api_controller, http_get

from ninja_jwt import authentication


@api_controller("/test-view", auth=authentication.JWTAuth())
class TestAPIController:
    @http_get("/test", url_name="test_view")
    def test(self):
        return {"foo": "bar"}


if not django.VERSION < (3, 1):

    @api_controller("/test-view-async", auth=authentication.AsyncJWTAuth())
    class TestAPIAsyncController:
        @http_get("/test-async", url_name="test_view")
        async def test(self):
            return {"foo": "bar"}
