## Unreleased

## Version 5.1.0

* Add back support for PyJWT 1.7.1 ([#536](https://github.com/jazzband/djangorestframework-simplejwt/pull/536))
* Make the token serializer configurable ([#521](https://github.com/jazzband/djangorestframework-simplejwt/pull/521))
* Simplify using custom token classes in serializers ([#517](https://github.com/jazzband/djangorestframework-simplejwt/pull/517))
* Fix default_app_config deprecation ([#415](https://github.com/jazzband/djangorestframework-simplejwt/pull/415))
* Add missing integration instructions for drf-yasg ([#505](https://github.com/jazzband/djangorestframework-simplejwt/pull/505))
* Add blacklist view to log out users ([#306](https://github.com/jazzband/djangorestframework-simplejwt/pull/306))
* Set default verifying key to empty str ([#487](https://github.com/jazzband/djangorestframework-simplejwt/pull/487))
* Add docs about TOKEN_USER_CLASS ([#455](https://github.com/jazzband/djangorestframework-simplejwt/pull/440))

Meta:
* Add auto locale updater ([#456](https://github.com/jazzband/djangorestframework-simplejwt/pull/456))

Translations:

* Added Korean translations ([#501](https://github.com/jazzband/djangorestframework-simplejwt/pull/501))
* Added Turkish translations ([#508](https://github.com/jazzband/djangorestframework-simplejwt/pull/508))

## Version 5.0.0

#### Breaking

* Set BLACKLIST_AFTER_ROTATION by default to False ([#455](https://github.com/jazzband/djangorestframework-simplejwt/pull/455))

#### Updates

* Remove verify from jwt.decode to follow PyJWT v2.2.0 ([#472](https://github.com/jazzband/djangorestframework-simplejwt/pull/472))
* Updated import list ([#459](https://github.com/jazzband/djangorestframework-simplejwt/pull/459))
* Repair generation of OpenAPI with Spectacular ([#452](https://github.com/jazzband/djangorestframework-simplejwt/pull/452))
* Add "iat" claim to token ([#192](https://github.com/jazzband/djangorestframework-simplejwt/pull/192))
* Add blacklist view to log out users ([#306](https://github.com/jazzband/djangorestframework-simplejwt/pull/306)) 

## Version 4.8.0

* Add integration instructions for drf-yasg ([#145](https://github.com/jazzband/djangorestframework-simplejwt/pull/145))
* Verify Serializer Should Honour Blacklist ([#239](https://github.com/jazzband/djangorestframework-simplejwt/pull/239))
* Added missing import in getting_started docs ([#431](https://github.com/jazzband/djangorestframework-simplejwt/pull/431))
* Use import_string for token_backend ([#435](https://github.com/jazzband/djangorestframework-simplejwt/pull/435))
* Add JWKS support ([#437](https://github.com/jazzband/djangorestframework-simplejwt/pull/435))
* Use pathlib instead of open in setup.py ([#339](https://github.com/jazzband/djangorestframework-simplejwt/pull/339))
* Optimize default_user_authentication_rule ([#441](https://github.com/jazzband/djangorestframework-simplejwt/pull/441))
* Add Leeway option to decode ([#445](https://github.com/jazzband/djangorestframework-simplejwt/pull/445))

## Version 4.7.2

* Fix BrowsableAPIRenderer needing `media_type` ([#426](https://github.com/jazzband/django-rest-framework-simplejwt/pull/426))
* Fix blacklist migrations for multiple databases ([#429](https://github.com/jazzband/django-rest-framework-simplejwt/pull/429))
* Fix Django 3.2 `default_app_config` deprecation ([#415](https://github.com/jazzband/django-rest-framework-simplejwt/pull/415))
* Fix docs specifying `INSTALLED_APPS` for SimpleJWT iff you want translations ([#420](https://github.com/jazzband/django-rest-framework-simplejwt/pull/420))
* Fix drf-yasg API Schema generation for `TokenRefreshSerializer` ([#396](https://github.com/jazzband/django-rest-framework-simplejwt/pull/396))
* Fix invalid syntax in docs for `INSTALLED_APPS` ([#416](https://github.com/jazzband/django-rest-framework-simplejwt/pull/416))

Translations:

* Added Dutch translations ([#422](https://github.com/jazzband/django-rest-framework-simplejwt/pull/422))
* Added Ukrainian translations ([#423](https://github.com/jazzband/django-rest-framework-simplejwt/pull/423))
* Added Simplified Chinese translations ([#427](https://github.com/jazzband/django-rest-framework-simplejwt/pull/427))

## Version 4.7.1

* Fixed user-generated migration file bug in token_blacklist ([#411](https://github.com/jazzband/django-rest-framework-simplejwt/pull/411))

## Version 4.7.0

* Added support for Django 3.2 and drop Django 3.0 ([#404](https://github.com/jazzband/django-rest-framework-simplejwt/pull/404))
* Added Italian translations ([#342](https://github.com/jazzband/django-rest-framework-simplejwt/pull/342))
* Fixed DRF app registry bug, specifically `django.core.exceptions.AppRegistryNotReady`
  ([#331](https://github.com/jazzband/django-rest-framework-simplejwt/pull/331))
* Fixed support for PyJWT>=2.0.0 ([#376](https://github.com/jazzband/django-rest-framework-simplejwt/pull/376))
* Migrated blacklist app models to use BigAutoField IDs for Django>=3.2. ([#404](https://github.com/jazzband/django-rest-framework-simplejwt/pull/404))

## Version 4.6

* Added support for PyJWT>=2.0.0 ([#329](https://github.com/jazzband/django-rest-framework-simplejwt/pull/329))
* Restored Python 3.7 support ([#332](https://github.com/jazzband/django-rest-framework-simplejwt/pull/332))
* Fixed Django 4.0 re_path deprecation ([#280](https://github.com/jazzband/django-rest-framework-simplejwt/pull/280))

Translations:
* Added Indonesian translations ([#316](https://github.com/jazzband/django-rest-framework-simplejwt/pull/316))

## Version 4.5

* Added `AUTH_HEADER_NAME` to settings ([#309](https://github.com/jazzband/django-rest-framework-simplejwt/pull/309))
* Added `USER_AUTHENTICATION_RULE` to settings ([#279](https://github.com/jazzband/django-rest-framework-simplejwt/pull/279))
* Added `UPDATE_LAST_LOGIN` to settings ([#238](https://github.com/jazzband/django-rest-framework-simplejwt/pull/238))
* Fixed packaging of locale folder for installation ([#117](https://github.com/jazzband/django-rest-framework-simplejwt/pull/117))
* Allowed TokenUser to be configurable ([#172](https://github.com/jazzband/django-rest-framework-simplejwt/pull/172))
* Dropped Python 3.7 and below (restored Python 3.7 but not 3.6 in next version) 
* Improved error message if cryptography isn't installed
  when developer tries to use a certain algorithm that needs the package
  ([#285](https://github.com/jazzband/django-rest-framework-simplejwt/pull/285))
* Fixed Django 4.0 ugettext_lazy deprecation warnings ([#186](https://github.com/jazzband/django-rest-framework-simplejwt/pull/186))
* Remove upper bound of Python version ([#225](https://github.com/jazzband/django-rest-framework-simplejwt/pull/225))
* Added DRF 3.11 support ([#230](https://github.com/jazzband/django-rest-framework-simplejwt/pull/230))

Translations:
* Added French translations ([#314](https://github.com/jazzband/django-rest-framework-simplejwt/pull/314))
* Added Spanish translations ([#294](https://github.com/jazzband/django-rest-framework-simplejwt/pull/294))
* Added Argentinian Spanish translations ([#244](https://github.com/jazzband/django-rest-framework-simplejwt/pull/244))
* Added Persian translations ([#220](https://github.com/jazzband/django-rest-framework-simplejwt/pull/220))
* Added German translations ([#198](https://github.com/jazzband/django-rest-framework-simplejwt/pull/198))
* Added Czech translations ([#188](https://github.com/jazzband/django-rest-framework-simplejwt/pull/188))
* Added Polish translations ([#166](https://github.com/jazzband/django-rest-framework-simplejwt/pull/166))
* Fixed incorrect language encoding from de_CH to es_CL ([#299](https://github.com/jazzband/django-rest-framework-simplejwt/pull/299))

## Version 4.4

* Added official support for Python 3.8 and Django 3.0.
* Added settings for expected audience and issuer claims.
* Documentation updates.
* Updated package/python version support (check the README to see what new
  versions are supported and what old ones are no longer supported!)
* Added Chilean Spanish language support.
* Added Russian language support.

## Version 4.3

* Added `JTI_CLAIM` setting to allow storing token identifiers under a
  different claim.

## Version 4.2

* We now return HTTP 401 for user not found or inactive.

## Version 4.1.5

* Restricted `setup.py` config to Python 3 only.

## Version 4.1.4

* Included translation files in release package.

## Version 4.1.3

* Updated `python-jose` version requirement.

## Version 4.1.2

* Fixed `KeyError` in `TokenObtainSerializer.validate`.

## Version 4.1.1

* Added request pass-through on `django.contrib.auth.authenticate` call in
  `TokenObtainSerializer`.
* Updated `TokenObtainSerializer` to use `fail` API from parent class.

## Version 4.1

* Added language support for Brazilian Portuguese.
* Added support for automatic username lookup in `TokenUser`.

## Version 4.0

* Removed Python 2 support.
* Fixed crash when empty AUTHORIZATION header is sent.
* Fixed testing DB transaction issues.
* Simplified/improved testing and dev setup.
* Switched to using bumpversion for release process.

## Version 3.3

* Removed official support for Python 3.4.
* Added support for Python 3.7.
* Added support for Django 2.1.
* Added support for DRF 3.9.

## Version 3.2.3

* Fixed issue with `WWW-Authenticate` header not being included in 401
  responses.

## Version 3.2.2

* Added missing method `get` on `Token` base class.

## Version 3.2.1

* Simplified some blacklist app code.
* Resolved possible race condition.

## Version 3.2

* Added ``TokenObtainSerializer.get_token`` method to facilitate customization
  of token claims.
* Added ``TokenVerifyView`` to allow verification of HMAC-signed tokens by API
  users who have no access to the signing key.
* Renamed ``AUTH_HEADER_TYPE`` setting to ``AUTH_HEADER_TYPES``.  This setting
  now contains either a single valid auth header type or a list or tuple of
  valid auth header types.  If authentication fails, and more than one string is
  present in this tuple or list, the first item in the list will be used to
  build the "WWW-Authenticate" header in the response.

## Version 3.1

* Moved handling of TokenError exceptions from inside of serializer `validate`
  methods into token view `post` methods.

## Version 3.0

* Added support for refresh token rotation via ``ROTATE_REFRESH_TOKENS`` and
  ``BLACKLIST_AFTER_ROTATION`` settings.  See README for details.
* Added `BlacklistMixin.blacklist` method to make it easier to blacklist tokens
  regardless of whether or not they are present in the outstanding token list.
* In token blacklist app, changed `OutstandingToken.jti` field to char field to
  better reflect JWT spec.
* Renamed `AUTH_TOKEN_CLASS` setting to `AUTH_TOKEN_CLASSES`.  This setting now
  specifies a list of token classes (or class paths) which are used to verify
  tokens which are submitted for authorization.  This will hopefully help
  anyone wishing to gradually migrate between using different token types.
* Removed support for extensible JWT backends.  We're just going to use PyJWT
  exclusively to simplify things.
* Added support for more crypto algorithms.  All HMAC and RSA variants from
  PyJWT now supported.
* Renamed `SECRET_KEY` setting to `SIGNING_KEY`.
* The renamed `SIGNING_KEY` setting now acts doubly as a symmetric
  signing/verification key for HMAC algorithms and as a private key for RSA
  algorithms.
* Added `VERIFYING_KEY` setting for use with RSA algorithms.
* Removed undocumented `TOKEN_BACKEND_CLASS` setting.

## Version 2.1

* Switched to using [PyJWT](https://github.com/jpadilla/pyjwt) as the
  underlying library for signing and verifying tokens.
