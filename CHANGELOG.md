## 5.5.1

Missing Migration for rest_framework_simplejwt.token_blacklist app. A previously missing migration (0013_blacklist) has now been added. This issue arose because the migration file was mistakenly not generated earlier. This migration was never part of an official release, but users following the latest master branch may have encountered it.

**Notes for Users**
If you previously ran makemigrations in production and have a 0013_blacklist migration in your django_migrations table, follow these steps before upgrading:

1. Roll back to the last known migration:
```bash
python manage.py migrate rest_framework_simplejwt.token_blacklist 0012
```
2. Upgrade djangorestframework-simplejwt to the latest version.
3. Apply the migrations correctly:
```bash
python manage.py migrate
```
**Important**: If other migrations depend on 0013_blacklist, be cautious when removing it. You may need to adjust or regenerate dependent migrations to ensure database integrity.

* fix:  add missing migration for token_blacklist app by @juanbailon in https://github.com/jazzband/djangorestframework-simplejwt/pull/894
* :globe_with_meridians: Fix typos and improve clarity in es_AR translations by @fabianfalon in https://github.com/jazzband/djangorestframework-simplejwt/pull/876
* docs: Add warning in docs for `for_user` usage by @vgrozdanic in https://github.com/jazzband/djangorestframework-simplejwt/pull/872
* feat: log warning if token is being created for inactive user by @vgrozdanic in https://github.com/jazzband/djangorestframework-simplejwt/pull/873
* ref: full tracebacks on exceptions by @vgrozdanic in https://github.com/jazzband/djangorestframework-simplejwt/pull/870
* #858 New i18n messages by @Cloves23 in https://github.com/jazzband/djangorestframework-simplejwt/pull/879
* Repair the type annotations in the TokenViewBase class. by @triplepoint in https://github.com/jazzband/djangorestframework-simplejwt/pull/880
* fix: Token.outstand forces users to install blacklist app by @Andrew-Chen-Wang in https://github.com/jazzband/djangorestframework-simplejwt/pull/884
* fix: PytestConfigWarning Unknown config option: python_paths by @vgrozdanic in https://github.com/jazzband/djangorestframework-simplejwt/pull/886
* fix: Do not copy `iat` claim from refresh token by @vgrozdanic in https://github.com/jazzband/djangorestframework-simplejwt/pull/888
* fix:  add missing migration for token_blacklist app by @juanbailon in https://github.com/jazzband/djangorestframework-simplejwt/pull/894
* Update Persian translations (fa, fa_IR) for Django application by @mahdirahimi1999 in  https://github.com/jazzband/djangorestframework-simplejwt/pull/897

## 5.5.0
* Cap PyJWT version to <2.10.0 to avoid incompatibility with subject claim type requirement by @grayver in https://github.com/jazzband/djangorestframework-simplejwt/pull/843
* Add specific "token expired" exceptions by @vainu-arto in https://github.com/jazzband/djangorestframework-simplejwt/pull/830
* Fix user_id type mismatch when user claim is not pk by @jdg-journeyfront in https://github.com/jazzband/djangorestframework-simplejwt/pull/851
* Caching signing key by @henryfool91 in https://github.com/jazzband/djangorestframework-simplejwt/pull/859
* Adds new refresh tokens to OutstandingToken db. by @thecarpetjasp in https://github.com/jazzband/djangorestframework-simplejwt/pull/866

## 5.4.0
* Changed string formatting in views by @Egor-oop in https://github.com/jazzband/djangorestframework-simplejwt/pull/750
* Enhance BlacklistMixin with Generic Type for Accurate Type Inference by @Dresdn in https://github.com/jazzband/djangorestframework-simplejwt/pull/768
* Improve type of `Token.for_user` to allow subclasses by @sterliakov in https://github.com/jazzband/djangorestframework-simplejwt/pull/776
* Fix the `Null` value of the `OutstandingToken` of the `BlacklistMixin.blacklist` by @JaeHyuckSa in https://github.com/jazzband/djangorestframework-simplejwt/pull/806
* Fix: Disable refresh token for inactive user. by @ajay09 in https://github.com/jazzband/djangorestframework-simplejwt/pull/814
* Add option to allow inactive user authentication and token generation by @zxkeyy in https://github.com/jazzband/djangorestframework-simplejwt/pull/834
* Drop Django <4.2, DRF <3.14, Python <3.9 by @Andrew-Chen-Wang in https://github.com/jazzband/djangorestframework-simplejwt/pull/839
  * Note, many deprecated versions are only officially not supported but probably still work fine.
* Add support for EdDSA and other algorithms in jwt.algorithms.requires_cryptography (#822) https://github.com/jazzband/djangorestframework-simplejwt/pull/823

## 5.3.1

## What's Changed
* Remove EOL Python, Django and DRF version support by @KOliver94 in [#754](https://github.com/jazzband/djangorestframework-simplejwt/pull/754)
* Declare support for type checking (closes #664) by @PedroPerpetua in [#760](https://github.com/jazzband/djangorestframework-simplejwt/pull/760)
* Remove usages of deprecated datetime.utcnow() and datetime.utcfromtimestamp() in [#765](https://github.com/jazzband/djangorestframework-simplejwt/pull/765)

#### Translation Updates:
* Update Korean translations by @TGoddessana in https://github.com/jazzband/djangorestframework-simplejwt/pull/753

## 5.3.0

#### Notable Changes:
* Added support for Python 3.11 by @joshuadavidthomas [#636](https://github.com/jazzband/djangorestframework-simplejwt/pull/636)
* Added support for Django 4.2 by @johnthagen [#711](https://github.com/jazzband/djangorestframework-simplejwt/pull/711)
* Added support for DRF 3.14 by @Andrew-Chen-Wang [#623](https://github.com/jazzband/djangorestframework-simplejwt/pull/623)
* Added Inlang to facilitate community translations by @jannesblobel [#662](https://github.com/jazzband/djangorestframework-simplejwt/pull/662)
* Revoke access token if user password is changed by @mahdirahimi1999 [#719](https://github.com/jazzband/djangorestframework-simplejwt/pull/719)
* Added type hints by @abczzz13 [#683](https://github.com/jazzband/djangorestframework-simplejwt/pull/683)
* Improved testing by @kiraware [#688](https://github.com/jazzband/djangorestframework-simplejwt/pull/688)
* Removed support for Django 2.2 by @kiraware [#688](https://github.com/jazzband/djangorestframework-simplejwt/pull/688)

#### Documentation:
* Added write_only=True to TokenBlacklistSerializer's refresh field for better doc generation by @Yaser-Amiri [#699](https://github.com/jazzband/djangorestframework-simplejwt/pull/699)
* Updated docs on serializer customization by @2ykwang [#668](https://github.com/jazzband/djangorestframework-simplejwt/pull/668)

#### Translation Updates:
* Updated translations for Persian (fa) language by @mahdirahimi1999 [#723](https://github.com/jazzband/djangorestframework-simplejwt/pull/723) and https://github.com/jazzband/djangorestframework-simplejwt/pull/708
* Updated translations for Indonesian (id) language by @kiraware [#685](https://github.com/jazzband/djangorestframework-simplejwt/pull/685)
* Added Arabic language translations by @iamjazzar [#690](https://github.com/jazzband/djangorestframework-simplejwt/pull/690)
* Added Hebrew language translations by @elam91 [#679](https://github.com/jazzband/djangorestframework-simplejwt/pull/679)
* Added Slovenian language translations by @banDeveloper [#645](https://github.com/jazzband/djangorestframework-simplejwt/pull/645)

## Version 5.2.2

Major security release

* Revert #605 [#629](https://github.com/jazzband/djangorestframework-simplejwt/pull/629)
* Fix typo in blacklist_app.rst by @cbscsm [#593](https://github.com/jazzband/djangorestframework-simplejwt/pull/593)

## Version 5.2.1

* Add Swedish translations by @PasinduPrabhashitha [#579](https://github.com/jazzband/djangorestframework-simplejwt/pull/579)
* Fixed issue #543 by @armenak-baburyan [#586](https://github.com/jazzband/djangorestframework-simplejwt/pull/586)
* Fix uncaught exception with JWK by @jerr0328 [#600](https://github.com/jazzband/djangorestframework-simplejwt/pull/600)
* Test on Django 4.1 by @2ykwang [#604](https://github.com/jazzband/djangorestframework-simplejwt/pull/604)

## Version 5.2.0

* Remove the JWTTokenUserAuthentication from the Experimental Features #546 by @byrpatrick [#547](https://github.com/jazzband/djangorestframework-simplejwt/pull/547)
* Fix leeway type error by @2ykwang [#554](https://github.com/jazzband/djangorestframework-simplejwt/pull/554)
* Add info on TokenBlacklistView to the docs by @inti7ary [#558](https://github.com/jazzband/djangorestframework-simplejwt/pull/558)
* Update JWTStatelessUserAuthentication docs by @2ykwang [#561](https://github.com/jazzband/djangorestframework-simplejwt/pull/561)
* Allow none jti claim token type claim by @denniskeends [#567](https://github.com/jazzband/djangorestframework-simplejwt/pull/567)
* Allow customizing token JSON encoding by @vainu-arto [#568](https://github.com/jazzband/djangorestframework-simplejwt/pull/568)

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
