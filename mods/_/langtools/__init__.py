from collections.abc import Callable

from tcrutils.console import c

#    vvvvvvvv
from _.config import S

#    ^^^^^^^^
# absolute path required due to python import machinery shenanigans
# NOTE: I sincerely HOPE python works like: that once '_' is in sys.modules it will not go looking for it somewhere and crash if the order of imported modules is different or whatnot


def subclass_values[V1, V2](fn: Callable[[V1], V2], /, **d: V1) -> dict[str, V2]:
	return {k: fn(v) for k, v in d.items()}


def subclass_keys[V](fn: Callable[[str], str], /, **d: V) -> dict[str, V]:
	return {fn(k): v for k, v in d.items()}


def subclass_items[V1, V2](fn: Callable[[str, V1], tuple[str, V2]], /, **d: V1) -> dict[str, V2]:
	return {(fn_retval := fn(k, v))[0]: fn_retval[1] for k, v in d.items()}
