"""General Commands"""

import discord
from discord.ext import commands
from main import app_name
from io import BytesIO, StringIO
import requests
import bs4
import re
import os
import subprocess
from cogs.utils import checks
from AWSMapConverter.awmap import AWMap

config = f"{app_name}:maps"


re_awl = re.compile(r"(http[s]?:\/\/)?awbw.amarriner.com\/(glenstorm\/)?prevmaps.php\?maps_id=([0-9]+)(?i)")
re_csv = re.compile(r"(([0-9])+(,[0-9]*)*(\n[0-9]+(,[0-9]*)*)*){1}")


class Maps:
    """General use and utility commands."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.listen_for_maps = False
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

        aws = await self.get_aws(awmap)
        csv = await self.get_awbw(awmap)
        minimap = await self.get_minimap(awmap)
        embed = self.format_embed(ctx, awmap.title, author=author, aws=aws, minimap=minimap, csv=csv)
        await ctx.send(embed=embed)

    ##########################
    # Some Utility Functions #
    ##########################

    async def get_hosted_file(self, file: discord.File):
        msg = await self.buffer_channel.send(file=file)
        return msg.attachments[0].url

    async def check_map(self, msg: discord.Message, title: str=None):
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
                    awbw_string = StringIO()
                    attachment.save(fp=awbw_string)
                    awbw_string.seek(0)
                    awmap = AWMap().from_awbw(awbw_string.read())  # TODO: Need to check discord.File
                    return awmap
                except AssertionError:
                    return  # TODO: Error message: Invalid AWBW CSV
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
                    return self.open_awbw_map_id(search.group(3))
            else:
                try:
                    search = re_csv.search(msg.content)
                    if search:
                        awmap = AWMap().from_awbw(search.group(0), title)
                        return awmap
                except AssertionError:
                    return

    def open_aws(self, aws: bytes):
        return AWMap().from_aws(aws)

    def open_awbw_map_id(self, awbw_id):
        r_text = requests.get(f"http://awbw.amarriner.com/text_map.php?maps_id={awbw_id}")
        soup_text = bs4.BeautifulSoup(r_text.text, "html.parser")
        title_href = soup_text.find_all("a", href=f"prevmaps.php?maps_id={awbw_id}")

        if len(title_href) == 0:
            return

        map_url = f"http://awbw.amarriner.com/prevmaps.php?maps_id={awbw_id}"

        r_map = requests.get(map_url)
        soup_map = bs4.BeautifulSoup(r_map.text, "html.parser")
        # author = soup_map.select('a[href*="profile.php"]')[0].contents[0]
        author = soup_map.find(href=lambda href: href and re.compile("profile.php").search(href)).contents[0]

        title = title_href[0].contents[0]
        table = title_href[0].find_previous("table")
        map_csv = "\n".join([t.contents[0] for t in table.find_all_next("td")[2:]])

        awmap = AWMap().from_awbw(map_csv, title=title)
        awmap.author = author
        awmap.desc = map_url
        awmap.awbw_id = awbw_id

        return awmap

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
                                   f"[{author}](http://awbw.amarriner.com/profile.php?username={author})"

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
                    msg.content = f"{self.bot.command_prefix} {search.group(3)}"
                    await self.bot.process_commands(msg)


def setup(bot):
    Maps.pull()
    bot.add_cog(Maps(bot))
