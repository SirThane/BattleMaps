"""Commands for Advance Wars Maps"""

import discord
from discord.ext import commands
from main import app_name
from io import BytesIO
import re
import os
import subprocess
from datetime import datetime
from asyncio import sleep
from urllib.parse import quote
from cogs.utils import checks
from AWSMapConverter.awmap import AWMap
from cogs.utils.errors import *

config = f"{app_name}:maps"


re_awl = re.compile(r"(http[s]?:\/\/)?awbw.amarriner.com\/(glenstorm\/)?prevmaps.php\?maps_id=([0-9]+)(?i)")
re_csv = re.compile(r"(([0-9])+(,[0-9]*)*(\n[0-9]+(,[0-9]*)*)*){1}")


class Maps:
    """
    Commands for working with Advance Wars maps.
    Will currently support AWS map files and
    AWBW maps, both text, file, and links.
    Other features soon to come™
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.listen_for_maps = self.db.get(f"{config}:listen_for_maps") or False
        self.buffer_channel = self.bot.get_channel(id=434551085185630218)
        self.loaded_maps = {}

    @commands.group(name="map", invoke_without_command=True)
    async def _map(self, ctx, *, arg: str=""):  # TODO: if loaded map: info else: load
        ctx.message.content = f"{self.bot.command_prefix[0]}map info {arg}"
        await self.bot.process_commands(ctx.message)

    @_map.command(name="load")
    async def _load(self, ctx, title: str=None, *, arg: str=""):
        awmap = await CheckMap.check(ctx.message, title)

        if not awmap:
            raise InvalidMapException

    @_map.command(name="info")
    async def _info(self, ctx, title: str=None, *, arg: str=""):
        awmap = await CheckMap.check(ctx.message, title)

        if not awmap:
            raise InvalidMapException

        author = awmap.author
        awbw_id = awmap.awbw_id

        aws = await self.get_aws(awmap)
        csv = await self.get_awbw(awmap)
        minimap = await self.get_minimap(awmap)

        embed = self.format_embed(ctx, awmap.title, author=author, aws=aws, minimap=minimap, csv=csv, awbw_id=awbw_id)
        await ctx.send(embed=embed)

    ##########################
    # Some Utility Functions #
    ##########################

    async def timed_store(self, user: discord.Member, awmap: AWMap):
        """
        Stores an AWMap by user ID with a expiry of 5 minutes.
        Loading another map will reset the timer.

        :param user: `discord.Member` instance of command author
        :param awmap: `AWMap` instance of map loaded by `user`
        """
        ts = datetime.utcnow()
        self.loaded_maps[user.id] = {
            "ts": ts,
            "awmap": awmap
        }
        await sleep(300)
        if self.loaded_maps[user.id]["ts"] == ts:
            self.loaded_maps.pop(user.id)

    async def get_hosted_file(self, file: discord.File):
        msg = await self.buffer_channel.send(file=file)
        return msg.attachments[0].url

    def open_aws(self, aws: bytes):
        return AWMap().from_aws(aws)

    async def get_aws(self, awmap: AWMap):
        if awmap.title:
            title = awmap.title
        else:
            title = "Untitled"
        attachment = discord.File(fp=BytesIO(awmap.to_aws), filename=f"{title}.aws")
        url = await self.get_hosted_file(attachment)
        return url

    async def get_awbw(self, awmap: AWMap):
        if awmap.title:
            title = awmap.title
        else:
            title = "Untitled"
        attachment = discord.File(fp=BytesIO(awmap.to_awbw.encode("utf-8")), filename=f"{title}.csv")
        url = await self.get_hosted_file(attachment)
        return url

    async def get_minimap(self, awmap):
        if awmap.title:
            title = awmap.title
        else:
            title = "Untitled"
        img = BytesIO()
        awmap.minimap.save(img, "GIF", save_all=True)
        img.seek(0)
        attachment = discord.File(fp=img, filename=f"{title}.gif")
        url = await self.get_hosted_file(attachment)
        return url

    def _color(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return 0
        else:
            return ctx.me.color.value

    def format_embed(self, ctx, title, **kwargs):
        awbw_id = kwargs.get("awbw_id")
        author = kwargs.get("author")
        aws = kwargs.get("aws")
        minimap = kwargs.get("minimap")
        csv = kwargs.get("csv")

        embed = {
            "title": title,
            "description": "",
            "color": self._color(ctx),
        }

        if awbw_id:
            embed["url"] = f"http://awbw.amarriner.com/prevmaps.php?maps_id={awbw_id}"

        if minimap:
            embed["image"] = {"url": minimap}

        if author:
            embed["description"] = f"Design map by " \
                                   f"[{author}]({quote(f'http://awbw.amarriner.com/profile.php?username={author}')})"

        embed["fields"] = []

        if aws:
            embed["fields"] += [{"name": "AWS Download:",
                                 "value": f"[{title}]({aws})",
                                 "inline": True}]

        if csv:
            embed["fields"] += [{"name": "AWBW Text Map",
                                 "value": f"[{title}]({csv})",
                                 "inline": True}]

        return discord.Embed.from_data(embed)

    @checks.awbw_staff()
    @_map.command(name="listen", hidden=True)
    async def listen(self, ctx, *, arg):
        if arg.strip(" ").lower() in "on yes true y t".split(" "):
            self.db.set(f"{config}:listen_for_maps", True)
            self.listen_for_maps = True
        elif arg.strip(" ").lower() in "off no false n f".split(" "):
            self.db.set(f"{config}:listen_for_maps", False)
            self.listen_for_maps = False
        em = discord.Embed(color=self._color(ctx), title="BattleMaps Config",
                           description=f"Active Listen For Maps: `{self.listen_for_maps}`")
        await ctx.send(embed=em)

    @checks.sudo()
    @_map.command(name="update", hidden=True)
    async def _update(self, ctx):
        if self.pull():
            await ctx.send("Converter core updated.\nReloading cog.")
            self.bot.remove_cog(Maps(self.bot))
            self.bot.add_cog(Maps(self.bot))
        else:
            await ctx.send("Converter core already up-to-date.")

    @staticmethod
    def pull():
        cmd = "git -C AWSMapConverter --no-pager pull".split(" ")
        params = {
            "universal_newlines":   True,
            "cwd":                  os.getcwd(),
            "stdout":               subprocess.PIPE,
            "stderr":               subprocess.STDOUT
        }
        ret = subprocess.run(cmd, **params)
        if "up-to-date" in ret.stdout:
            return False
        elif "fatal: Not a git repository" in ret.stdout:
            cmd = "git clone --no-pager https://github.com/SirThane/AWSMapConverter.git".split(" ")
            subprocess.run(cmd, **params)
            return True
        else:
            return True

    async def on_message(self, msg):
        if self.listen_for_maps:
            if not msg.content.startswith(self.bot.command_prefix[0]):
                search = re_awl.search(msg.content)
                if search:
                    msg.content = f"{self.bot.command_prefix[0]}map {search.group(3)}"
                    await self.bot.process_commands(msg)


class CheckMap:
    """Takes a discord.Message object and checks
    for valid maps that can be loaded."""

    @staticmethod
    async def check(msg: discord.Message, title="[Untitled]", skips=None):

        if msg.attachments:
            attachment = msg.attachments[0]
            filename, ext = os.path.splitext(attachment.filename)

            if "aws" not in skips and ext == ".aws":
                return await CheckMap.from_aws(attachment)

            if "text" not in skips and ext.lower() in [".txt", ".csv"]:
                return await CheckMap.from_text(attachment, filename)

        s_awl = re_awl.search(msg.content)

        if "link" not in skips and s_awl:
            return CheckMap.from_id(s_awl.group(3))

        s_csv = re_awl.search(msg.content)

        if s_csv:

            if "msg_csv" not in skips and 0 <= int(s_csv.group(0).split(",")[0]) <= 176:
                return CheckMap.from_csv(s_csv.group(0), title)

            if "id" not in skips:
                return CheckMap.from_id(s_csv.group(0))


    @staticmethod
    async def from_aws(attachment):
        aws_bytes = BytesIO()
        await attachment.save(fp=aws_bytes)
        aws_bytes.seek(0)
        return AWMap().from_aws(aws_bytes.read())

    @staticmethod
    async def from_text(attachment, filename):
        awbw_bytes = BytesIO()
        await attachment.save(fp=awbw_bytes)
        awbw_bytes.seek(0)
        map_csv = awbw_bytes.read().decode("utf-8")
        try:
            awmap = AWMap().from_awbw(map_csv, title=filename)
        except AssertionError:
            raise AWBWDimensionsException
        else:
            return awmap

    @staticmethod
    def from_id(awbw_id):
        try:
            int(awbw_id)
        except Exception:
            raise InvalidMapException
        else:
            return AWMap().from_awbw(awbw_id=awbw_id)

    @staticmethod
    def from_csv(msg_csv, title):
        try:
            return AWMap().from_awbw(data=msg_csv, title=title)
        except AssertionError:
            raise AWBWDimensionsException


def setup(bot):
    Maps.pull()
    bot.add_cog(Maps(bot))
