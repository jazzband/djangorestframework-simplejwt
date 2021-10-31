def pytest_configure():
    from django.conf import settings

    MIDDLEWARE = (
        "django.middleware.common.CommonMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    )

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
            "other": {"ENGINE": "django.db.backends.sqlite3", "NAME": "other"},
        },
        SITE_ID=1,
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL="/static/",
        ROOT_URLCONF="tests.urls",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
            },
        ],
        MIDDLEWARE=MIDDLEWARE,
        MIDDLEWARE_CLASSES=MIDDLEWARE,
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "ninja_extra",
            "ninja_jwt",
            "ninja_jwt.token_blacklist",
            "tests",
        ),
        PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
        SIMPLE_JWT={
            "BLACKLIST_AFTER_ROTATION": True,
        },
    )

    try:
        import django

        django.setup()
    except AttributeError:
        pass
