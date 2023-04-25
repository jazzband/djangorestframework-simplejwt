import sys

try:
    if sys.version_info >= (3, 8):
        from importlib import metadata
    else:
        import importlib_metadata as metadata

    __version__ = metadata.version("djangorestframework_simplejwt")
except DistributionNotFound:
    # package is not installed
    __version__ = None
