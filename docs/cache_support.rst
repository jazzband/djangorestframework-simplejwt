Cache Support
==============

SimpleJWT provides optional cache support for improving performance. 
Currently, caching is available for:

- Blacklisted refresh tokens
- Blacklisted token families

To enable caching in SimpleJWT, you must first configure Django's ``CACHES`` setting:

.. code-block:: python

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-name",
        },
        "redis": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

In this example, two cache backends are defined. You can choose which one to use by 
setting the ``SJWT_CACHE_NAME`` option in your SimpleJWT configuration. For this case, 
it could be either `"default"` or `"redis"`.

.. Note::
    Ensure that your Django `CACHES` setting includes a cache matching the alias 
    defined by `SJWT_CACHE_NAME`.


Blacklist Cache
----------------

When enabled via the appropriate settings, blacklisted refresh tokens and token families
will be cached. This reduces the number of database queries when verifying whether a token
or family is blacklisted.

.. code-block:: python

    SIMPLE_JWT = {
        ...

        "SJWT_CACHE_NAME": "default",
        "CACHE_BLACKLISTED_REFRESH_TOKENS": True,
        "CACHE_BLACKLISTED_FAMILIES": True,
        "CACHE_TTL_BLACKLISTED_REFRESH_TOKENS": 3600, #time in seconds
        "CACHE_TTL_BLACKLISTED_FAMILIES": 3600, #time in seconds
        "CACHE_KEY_PREFIX_BLACKLISTED_REFRESH_TOKENS": "sjwt_brt",
        "CACHE_KEY_PREFIX_BLACKLISTED_FAMILIES": "sjwt_btf",

        ...
    }


Cache keys follow this format:

- Refresh token: ``sjwt_brt:<jti>``
- Token family: ``sjwt_btf:<family_id>``

