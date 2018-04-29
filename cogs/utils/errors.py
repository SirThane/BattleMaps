"""Custom Exception definitions"""


from discord.ext import commands


class AWBWDimensionsError(commands.CommandError):
    """Exception raised when an AWBW text map with
    an inconsistent amount of columns in its rows.
    Catch the AssertionError raised by the converter
    and raise this Exception"""


class InvalidMapError(commands.CommandError):
    """Exception raised when `check_map()` fails
    to return an `AWMap` instance."""


class NoLoadedMapError(commands.CommandError):
    """Exception raised when a command requiring
    a loaded map is invoked by a user without a map
    loaded"""


class UnimplementedError(commands.CommandError):
    """Exception raised when a command is called
    using a feature that has not yet been
    implemented"""
