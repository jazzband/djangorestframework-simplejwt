## Version 1.5.1

* Version bump because pypi doesn't seem to let you update an existing
  version's files.

## Version 1.5

* Renamed `PAYLOAD_ID_FIELD` setting to `USER_ID_CLAIM` to keep more in line
  with JWT terminology.
* Removed `encode` and `decode` methods on
  `rest_framework_simplejwt.tokens.Token` class.  These operations are now
  handled by the chosen `TokenBackend` class.  Please note that the new
  `decode` method on `TokenBackend` does not check for the existence of an
  "exp" claim.  This check is now performed in the `Token.__init__` method.
* Added the `rest_framework_simplejwt.backends` module back into Simple JWT.
  This module will provide classes that act as compatibility layers to
  different JWT libraries.  Actual encoding and decoding of tokens is now
  handled by this module.  Some verification of tokens is performed as well but
  this can vary depending on the underlying JWT library that is used.
* Removed the `__getattr__` method definiton on the
  `rest_framework_simplejwt.module.TokenUser` class.  Having `__getattr__`
  behavior which deferred attribute access to the underlying JWT posed too much
  of a security risk.
* Renamed the `update_expiration` and `check_expiration` methods on
  `rest_framework_simplejwt.tokens.Token` to `set_exp` and `check_exp` to make
  the API for that class a bit more concise.
