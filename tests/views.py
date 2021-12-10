from ninja_extra import api_controller, http_get

from ninja_jwt import authentication


@api_controller("/test-view", auth=authentication.JWTAuth())
class TestAPIController:
    @http_get("/test", url_name="test_view")
    def test(self):
        return {"foo": "bar"}
