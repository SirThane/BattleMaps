# -*- coding: utf-8 -*-

from datetime import timedelta

from asyncio import sleep
from discord import Embed, Colour
from discord.ext.commands import command, Context
from discord.ext.commands.cog import Cog

from cogs.utils.classes import Bot


class Timer(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = bot.db
        self.config = f"{bot.APP_NAME}:timer"

        bot.loop.create_task(self._init_timed_events(bot))

    async def _init_timed_events(self, client: Bot):
        """Create a event task with a tick-rate of 1s

        Event will be dispatched every second with the
        number of seconds passed since cog load"""

        await self.bot.wait_until_ready()  # Wait for the bot to launch first
        client.secs = 0

        secs = 0  # Count number secs
        while True:
            client.dispatch("timer_update", secs)
            secs += 1
            client.secs = secs
            await sleep(1)

    @Cog.listener("on_timer_update")
    async def on_timer_update(self, secs: int):
        """Listener will be called every second with the
        number of seconds passed since cog load"""
        pass

    @command(name="uptime", enabled=True)
    async def uptime(self, ctx: Context):
        em = Embed(
            title=f"⏲ {self.bot.APP_NAME} Uptime",
            description=f"Shop's been open for:  `{str(timedelta(seconds=self.bot.secs))}`",
            colour=Colour.red()
        )
        await ctx.send(embed=em)


def setup(bot: Bot):
    bot.add_cog(Timer(bot))
