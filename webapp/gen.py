"""
Workaround to fix compatibility between tornado 4.2.1-3 and apispec 0.33.0-1.
"""

from tornado.gen import coroutine as tornado_coroutine


def coroutine(func, replace_callback=True):
    """Fixed coroutine annotation."""
    wrapper = tornado_coroutine(func, replace_callback=replace_callback) # pylint: disable=unexpected-keyword-arg
    wrapper.__wrapped__ = func
    wrapper.__tornado_coroutine__ = True
    return wrapper
