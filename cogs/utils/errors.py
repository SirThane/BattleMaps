"""Custom Exception definitions"""


from discord.ext import commands


class AWBWDimensionsException(commands.CommandError):
    """Exception raised when an AWBW text map with
    an inconsistent amount of columns in its rows.
    Catch the AssertionError raised by the converter
    and raise this Exception"""

    # def __init__(self, message=None, *args):
    #     super().__init__(message, *args)


class InvalidMapException(commands.CommandError):
    """Exception raised when `check_map()` fails
    to return an `AWMap` instance."""


class NoLoadedMapException(commands.CommandError):
    """Exception raised when a command requiring
    a loaded map is invoked by a user without a map
    loaded"""


class UnimplementedException(commands.CommandError):
    """Exception raised when a command is called
    using a feature that has not yet been
    implemented"""
