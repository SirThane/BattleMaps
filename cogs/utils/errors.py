"""Custom Exception definitions"""


from discord.ext import commands


class AWBWDimensionsException(commands.CommandError):
    """Exception"""
    def __init__(self, message=None, *args):
        super().__init__(message, *args)
