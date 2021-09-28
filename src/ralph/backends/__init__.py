"""Backends for Ralph"""

from enum import Enum, auto


class BackendTypes(Enum):
    """Backend types"""

    DATABASE = auto()
    LOGGING = auto()
    STORAGE = auto()
    STREAM = auto()
