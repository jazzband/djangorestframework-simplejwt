import warnings
from typing import Any

try:
    from django.urls import reverse, reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse, reverse_lazy  # NOQA


class RemovedInDjango20Warning(DeprecationWarning):
    pass


class CallableBool:  # pragma: no cover
    """
    An boolean-like object that is also callable for backwards compatibility.
    """

    do_not_call_in_templates = True

    def __init__(self, value) -> None:
        self.value = value

    def __bool__(self) -> bool:
        return self.value

    def __call__(self) -> Any:
        warnings.warn(
            "Using user.is_authenticated() and user.is_anonymous() as a method "
            "is deprecated. Remove the parentheses to use it as an attribute.",
            RemovedInDjango20Warning,
            stacklevel=2,
        )
        return self.value

    def __nonzero__(self):  # Python 2 compatibility
        return self.value

    def __repr__(self) -> str:
        return "CallableBool(%r)" % self.value

    def __eq__(self, other) -> bool:
        return self.value == other

    def __ne__(self, other) -> bool:
        return self.value != other

    def __or__(self, other) -> bool:
        return bool(self.value or other)

    def __hash__(self) -> Any:
        return hash(self.value)


CallableFalse = CallableBool(False)
CallableTrue = CallableBool(True)
