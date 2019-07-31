"""
Performs basic utilities functions.
"""
def health():
    """ Returns JSON with health of API. """
    return {"health": "ok"}, 200
