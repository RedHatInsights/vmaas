"""
Common classes for Webapp-utils.
"""


class Request:
    """General class for processing requests"""

    @staticmethod
    def format_exception(text, status_code):
        """Formats error message to desired format"""
        return {"error": [{"status": str(status_code), "detail": text}]}, status_code

    @classmethod
    def get(cls, **kwargs):
        "Answer GET request"
        try:
            return cls.handle_get(**kwargs)
        except Exception:  # pylint: disable=broad-except
            return cls.format_exception("Internal server error", 500)

    @classmethod
    def handle_get(cls, **kwargs):  # pragma: no cover
        """Implement in child classes"""
        raise NotImplementedError

    @classmethod
    def post(cls, **kwargs):
        """ Answer POST request. """
        return cls.handle_post(**kwargs)

    @classmethod
    def handle_post(cls, **kwargs):
        """ Implement in child classes """
        raise NotImplementedError
