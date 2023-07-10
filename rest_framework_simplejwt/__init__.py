import sys

try:
    if sys.version_info >= (3, 8):
        from importlib import metadata

        __version__ = metadata.version("djangorestframework_simplejwt")
    elif sys.version_info >= (3,7):
        import importlib_metadata as metadata

        __version__ = metadata.version("djangorestframework_simplejwt")
    else:
        from pkg_resources import DistributionNotFound, get_distribution

        __version__ = get_distribution("djangorestframework_simplejwt").version

except DistributionNotFound:
    # package is not installed
    __version__ = None
