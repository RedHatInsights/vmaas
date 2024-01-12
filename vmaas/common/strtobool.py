"""Module providing `strtobool` function as replacement of distutils.strtobool."""


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to bool.

    True values are y, yes, t, true, on and 1; false values are n, no, f, false, off and 0.
    Raises TypeError if `val` is not string.
    Raises ValueError if `val` is anything else.
    """
    if not isinstance(val, str):
        raise TypeError(f"`{val}` is not of type str")
    trues = ("y", "yes", "t", "true", "on", "1")
    falses = ("n", "no", "f", "false", "off", "0")

    val = val.lower()
    if val in trues:
        return True
    if val in falses:
        return False
    raise ValueError(f"`{val}` not in {trues + falses}")
