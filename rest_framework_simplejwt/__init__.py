from importlib.metadata import PackageNotFoundError, version
from typing import Union

__version__: Union[str, None]

try:
    __version__ = version("djangorestframework_simplejwt")
except PackageNotFoundError:
    # package is not installed
    __version__ = None
