from django import VERSION

if VERSION < (3, 2):
    default_app_config = "ninja_jwt.token_blacklist.apps.TokenBlacklistConfig"
