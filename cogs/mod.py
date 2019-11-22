
from asyncio import sleep
from discord import Member, Forbidden, HTTPException
from discord.ext.commands import command, has_permissions
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.message import Message

from utils.classes import Bot
from utils.utils import SubRedis


class Moderation(Cog):
    """Moderation commands"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.root_db = bot.db
        self.config = SubRedis(bot.db, f"{bot.APP_NAME}:mod")

        self.errorlog = bot.errorlog

    @has_permissions(manage_messages=True)
    @command(name="purge")
    async def purge(self, ctx: Context, limit: int = 10, author: Member = None):
        """Purges messages from a channel

        Default number of messages to purge is 10

        Optional member may be specified by ping or user ID after number
        of messages. Will delete only messages from user."""

        await ctx.message.delete()
        await sleep(0.1)

        check = None
        if author:
            def check(message: Message) -> bool:
                return message.author.id == author.id

            # ``purge(limit, check)`` will only delete messages from ``history(limit)`` that match ``check``
            # Use a larger ``history`` to find number of total messages in channel such that ``limit``
            # messages matching ``check`` will be deleted.
            count_msg = 0
            count_author = 0

            async for msg in ctx.channel.history(limit=200):
                count_msg += 1

                # Increment ``count_author`` toward ``limit``
                if msg.author.id == author.id:
                    count_author += 1

                    # Found the number of total messages in history that of a ``limit`` number of messages
                    # that match ``check``
                    if count_author == limit:
                        limit = count_msg
                        break

        try:
            await ctx.channel.purge(
                limit=limit,
                check=check,
                bulk=True
            )

        except Forbidden as error:
            await self.errorlog.send(error, ctx)

        except HTTPException as error:
            await self.errorlog.send(error, ctx)

        except Exception as error:
            await self.errorlog.send(error, ctx)


def setup(bot: Bot):
    """Moderation"""
    bot.add_cog(Moderation(bot))
