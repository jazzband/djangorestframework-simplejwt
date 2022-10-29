
The `JWTTokenUserAuth` backend\'s `authenticate` method does
not perform a database lookup to obtain a user instance. Instead, it
returns a `ninja_jwt.models.TokenUser` instance which acts as a
stateless user object backed only by a validated token instead of a
record in a database. This can facilitate developing single sign-on
functionality between separately hosted Django apps which all share the
same token secret key. To use this feature, add the
`ninja_jwt.authentication.JWTTokenUserAuth` backend (instead
of the default `JWTAuth` backend) to the Django Ninja Extra route definition

```python
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTTokenUserAuth


@api_controller
class MyController:
    @route.get('/some-endpoint', auth=JWTTokenUserAuth())
    def some_endpoint(self):
        pass

```
