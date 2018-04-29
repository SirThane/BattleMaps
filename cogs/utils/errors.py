"""Custom Exception definitions"""


from discord.ext.commands import CommandError


class AWBWDimensionsError(CommandError):
    """Exception raised when an AWBW text map with
    an inconsistent amount of columns in its rows.
    Catch the AssertionError raised by the converter
    and raise this Exception"""


class InvalidMapError(CommandError):
    """Exception raised when `check_map()` fails
    to return an `AWMap` instance"""


class NoLoadedMapError(CommandError):
    """Exception raised when a command requiring
    a loaded map is invoked by a user without a map
    loaded"""


class UnimplementedError(CommandError):
    """Exception raised when a command is called
    using a feature that has not yet been
    implemented"""


class FileSaveFailureError(CommandError):
    """Exception raised when a failure prevents an
    attachment from being saved"""
