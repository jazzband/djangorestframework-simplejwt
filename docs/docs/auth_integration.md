
Ninja JWT uses Django Ninja `HttpBearer` as a way to authenticate users reaching your api endpoint.
Authenticated user can be found in `request.user` or `request.auth`

### Route Authentication - Class Based

```python
from ninja_extra import APIController, router, route
from ninja_jwt.authentication import JWTAuth

@router('')
class MyController(APIController):
    @route.get('/some-endpoint', auth=JWTAuth())
    def some_endpoint(self):
        ...
```

### Route Authentication - Function Based

```python
from ninja import router
from ninja_jwt import JWTAuth

router = router('')

@router.get('/some-endpoint', auth=JWTAuth())
def some_endpoint(self):
    ...
```

Custom Auth Implement
-------
If you wish to use a different implementation of `JWTAuth`, then you need to inherit from `JWTBaseAuthentication`.
Please read more on [Django Ninja - Authentication](https://django-ninja.rest-framework.com/tutorial/authentication/), if you want to use a different approach that is not `bearer`.

example:
```python
from ninja.security import APIKeyHeader
from ninja_jwt.authentication import JWTBaseAuthentication
from ninja import router

class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        if key == "supersecret":
            return self.jwt_authenticate(request, token=key)


header_key = ApiKey()
router = router('')

@api.get("/headerkey", auth=header_key)
def apikey(request):
    return f"Token = {request.auth}"

```