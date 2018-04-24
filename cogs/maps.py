"""General Commands"""

import discord
from discord.ext import commands
from main import app_name
from io import BytesIO, StringIO
import re
import os
import subprocess
from urllib.parse import quote
from cogs.utils import checks
from AWSMapConverter.awmap import AWMap
from cogs.utils.errors import *

config = f"{app_name}:maps"


re_awl = re.compile(r"(http[s]?:\/\/)?awbw.amarriner.com\/(glenstorm\/)?prevmaps.php\?maps_id=([0-9]+)(?i)")
re_csv = re.compile(r"(([0-9])+(,[0-9]*)*(\n[0-9]+(,[0-9]*)*)*){1}")


class Maps:
    """General use and utility commands."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.listen_for_maps = self.db.get(f"{config}:listen_for_maps") or False
        self.buffer_channel = self.bot.get_channel(id=434551085185630218)

    @commands.group(name="map", invoke_without_command=True)
    async def _map(self, ctx, *, arg: str=""):
        ctx.message.content = f"{self.bot.command_prefix[0]}map info {arg}"
        await self.bot.process_commands(ctx.message)

    @_map.command(name="info")
    async def _info(self, ctx, title: str=None, *, arg: str=""):
        awmap = await self.check_map(ctx.message, title)

        if not awmap:
            await ctx.send("Invalid Map")  # TODO: Prettify
            return

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

    async def get_hosted_file(self, file: discord.File):
        msg = await self.buffer_channel.send(file=file)
        return msg.attachments[0].url

    async def check_map(self, msg: discord.Message, title: str=None):  # TODO: This whole bitch gon get a refactor
        if msg.attachments:
            attachment = msg.attachments[0]
            filename, ext = os.path.splitext(attachment.filename)
            if ext.lower() == ".aws":
                aws_bytes = BytesIO()
                await attachment.save(fp=aws_bytes)
                aws_bytes.seek(0)
                return AWMap().from_aws(aws_bytes.read())
            elif ext.lower() in [".txt", ".csv"]:
                try:
                    awbw_bytes = BytesIO()
                    await attachment.save(fp=awbw_bytes)
                    awbw_bytes.seek(0)
                    map_csv = awbw_bytes.read().decode("utf-8")
                    awmap = AWMap().from_awbw(map_csv, title=filename)  # TODO: Need to check discord.File
                    return awmap
                except AssertionError:
                    raise AWBWDimensionsException
                    # return  # TODO: Error message: Invalid AWBW CSV
        else:
            search = re_awl.search(msg.content)
            if search:
                try:
                    int(search.group(3))
                except ValueError:
                    return
                except TypeError:
                    return
                else:
                    return AWMap().from_awbw(awbw_id=search.group(3))
            else:
                try:
                    search = re_csv.search(msg.content)
                    if search and 0 <= int(search.group(0).split(",")[0]) <= 176:
                        awmap = AWMap().from_awbw(data=search.group(0), title=title)
                        return awmap
                    elif search:
                        try:
                            awbw_id = int(search.group(0))
                            return AWMap().from_awbw(awbw_id=awbw_id)
                        except ValueError:
                            return
                except AssertionError:
                    raise AWBWDimensionsException  # TODO: The converter core is catching AssertionError. Stop that.
                    # return

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


def setup(bot):
    Maps.pull()
    bot.add_cog(Maps(bot))
