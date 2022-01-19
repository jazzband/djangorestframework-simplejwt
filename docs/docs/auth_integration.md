
Ninja JWT uses Django Ninja `HttpBearer` as a way to authenticate users reaching your api endpoint.
Authenticated user can be found in `request.user` or `request.auth`

### Route Authentication - Class Based

```python
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

@api_controller
class MyController:
    @route.get('/some-endpoint', auth=JWTAuth())
    def some_endpoint(self):
        ...
```

### Route Authentication - Function Based

```python
from ninja import router
from ninja_jwt.authentication import JWTAuth

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

class ApiKey(APIKeyHeader, JWTBaseAuthentication):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        return self.jwt_authenticate(request, token=key)


header_key = ApiKey()
router = router('')

@router.get("/headerkey", auth=header_key)
def apikey(request):
    return f"Token = {request.auth}"

```

### Asynchronous Route Authentication
If you are interested in the Asynchronous Route Authentication, there is `AsyncJWTAuth` class

```python
from ninja_extra import api_controller, route
from ninja_jwt.authentication import AsyncJWTAuth

@api_controller
class MyController:
    @route.get('/some-endpoint', auth=AsyncJWTAuth())
    async def some_endpoint(self):
        ...
```
N:B `some_endpoint` must be asynchronous. Any endpoint function marked with `AsyncJWTAuth` must be asynchronous. 

!!! warning
    Asynchronous feature is only available for django version > 3.0