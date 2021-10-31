from ninja_extra import APIController, route, router

from ninja_jwt import authentication


@router("/test-view", auth=authentication.JWTAuth())
class TestAPIController(APIController):
    @route.get("/test", url_name="test_view")
    def test(self):
        return {"foo": "bar"}
