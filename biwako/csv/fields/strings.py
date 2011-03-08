from .base import Field


class String(Field):
    # CSV requires a file opened in text mode, which already handles
    # encoding conversions, and the CSV parser itself deals with things
    # like quotes, so there's really nothing interesting to do here.
    pass


