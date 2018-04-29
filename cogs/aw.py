"""Commands for Advance Wars Maps"""

import re
import os
import subprocess
from asyncio import sleep
from datetime import datetime
from io import BytesIO
from typing import Union
from urllib.parse import quote

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

from AWSMapConverter.awmap import AWMap
from cogs.utils import checks
from cogs.utils import errors
from main import APP_NAME


CONFIG = f"{APP_NAME}:maps"


RE_AWL = re.compile(
    r"(http[s]?://)?awbw.amarriner.com/(glenstorm/)"
    r"?prevmaps.php\?maps_id=([0-9]+)(?i)"
)
RE_CSV = re.compile(r"(([0-9])+(,[0-9]*)*(\n[0-9]+(,[0-9]*)*)*){1}")


class AdvanceWars:
    """
    Commands for working with Advance Wars maps.
    Will currently support AWS map files and
    AWBW maps, both text, file, and links.
    Other features soon to come™

    Maps can be automatically loaded from AWS,
    CSV, and AWBW links if `Map Listen` is turned
    on. See `[p]help map listen` for more details.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.listen_for_maps = self.db.get(
            f"{CONFIG}:listen_for_maps"
        ) or False
        self.buffer_channel = self.bot.get_channel(id=434551085185630218)
        self.loaded_maps = {}

    """
        #################################
        # General use commands for maps #
        #################################
    """

    @commands.group(
        name="map",
        invoke_without_command=True,
        usage="[map file or link]"
    )
    async def _map(self, ctx: Context, arg: str="", *, args: str=""):
        """The base command for working with maps

        This command will retrieve map information
        on a loaded map.

        This command will load a map if you do not
        already have one loaded.

        See `[p]help map load` for more information
        on loading maps."""

        if ctx.author.id in self.loaded_maps.keys():

            # Subcommands available to ctx.author
            avail_cmds = []

            for command in ctx.command.walk_commands():
                if await command.can_run(ctx):
                    avail_cmds.append(command.name)

            if arg in avail_cmds:
                ctx.message.content = f"{self._inv(ctx)} {arg} {args}"
                ctx = await self.bot.get_context(ctx.message)
                await self.bot.invoke(ctx)

            else:
                ctx.message.content = f"{self._inv(ctx)} info {arg} {args}"
                ctx = await self.bot.get_context(ctx.message)
                await self.bot.invoke(ctx)

        else:
            ctx.message.content = f"{self._inv(ctx)} load {arg} {args}"
            ctx = await self.bot.get_context(ctx.message)
            await self.bot.invoke(ctx)

    @_map.command(name="load", usage="[title]")
    async def _load(self, ctx: Context, title: str=None, *, _: str=""):
        """Load a map to be worked with

        This command will load a map to be worked with.

        You can load maps through 5 different methods:
        __AWS File__
        `[p]map load` with attached AWS file

        __AWBW Map CSV File__
        `[p]map load` with attached CSV or TXT file

        __AWBW Map Link__
        `[p]map load http://awbw.amarriner.com/prevmaps.php?maps_id=12345`

        __AWBW Map ID__
        `[p]map load 12345`

        __AWBW Text Style Map__
        `[p]map load "Example Map"`
        ```
        1,2,3,4,5
        6,7,8,9,10
        11,12,13,14,15
        16,17,18,19,20
        21,22,23,24,25
        ```
        For text maps, the first line must be the title.
        For multi-word titles, you must wrap the title
        in quotes (" " or ' '). You will receive an
        error if not all rows have the same number of
        columns. Markdown boxes are not necessary, but
        may make typing text maps easier.

        Text maps stay loaded as long as you're working
        with them with a time out of 5 minutes. After 5
        minutes with no activity, maps are automatically
        unloaded and must loaded again to continue
        working with them."""

        awmap = await CheckMap.check(ctx.message, title)

        if not awmap:
            raise errors.InvalidMapError

        await self.em_load(ctx.channel, awmap)
        await self.timed_store(ctx.author, awmap)

    @_map.command(name="download", usage=" ")
    async def download(self, ctx: Context, *, _: str=""):
        """Download your currently loaded map

        Use this command when you have a map loaded
        with `[p]map load` to get download links for
        all supported map formats.

        Currently supported formats:
        `Advance Wars Series Map Editor File (*.aws)`
        `Advance Wars By Web Text Map File (*.csv)`"""
        awmap = self.get_loaded_map(ctx.author)

        if not awmap:
            raise errors.NoLoadedMapError

        await self.em_download(ctx.channel, awmap)

    @_map.command(name="info", usage=" ")
    async def info(self, ctx: Context, *, _: str=""):
        """Something something information about a map"""
        raise errors.UnimplementedError

    """
        ##########################
        # Some Utility Functions #
        ##########################
    """

    async def timed_store(
            self,
            user: discord.Member,
            awmap: AWMap
    ):
        """
        Stores an AWMap by user ID with a expiry of 1 minute.
        Loading another map will reset the timer. Stored in
        `self.loaded_maps` dict with structure:

        user.id: {
            "awmap": awmap,
            "ts": datetime.utcnow()
            }

        :param user: `discord.Member` instance of command author
        :param awmap: `AWMap` instance of map loaded by `user`

        :returns: `None` (Does not return)
        """
        ts = datetime.utcnow()
        self.loaded_maps[user.id] = {
            "ts": ts,
            "awmap": awmap
        }
        await sleep(300)
        if self.loaded_maps[user.id]["ts"] == ts:
            self.loaded_maps.pop(user.id)

    def get_loaded_map(
            self,
            user: discord.Member
    ) -> Union[AWMap, None]:
        """Will retrieve loaded map object for a given user.

        :param user: `discord.Member` instance for user

        :return: `AWMap` object or `None` if no loaded map"""

        store = self.loaded_maps.get(user.id)

        if store:
            return store["awmap"]
        else:
            return None

    async def get_hosted_file(
            self,
            file: discord.File
    ) -> str:
        """Sends a message to Discord containing a file to
        return the file URL hosted on Discord

        :param file: `discord.File` object containing the file to host

        :return: `str` URL of hosted file"""
        msg = await self.buffer_channel.send(file=file)
        return msg.attachments[0].url

    async def get_aws(
            self,
            awmap: AWMap
    ) -> str:
        """Uses `AWMap`'s `to_aws` parameter to export a map
        as AWS file then returns a link to the file hosted on
        Discord using `get_hosted_file` method

        :param awmap: `AWMap` instance of map to export

        :return: `str` URL of hosted AWS file"""

        if awmap.title:
            title = awmap.title
        else:
            title = "Untitled"

        attachment = discord.File(
            fp=BytesIO(awmap.to_aws),
            filename=f"{title}.aws"
        )
        url = await self.get_hosted_file(attachment)

        return url

    async def get_awbw(
            self,
            awmap: AWMap
    ) -> str:
        """Uses `AWMap`'s `to_awbw` parameter to export a map
        to an AWBW CSV text file then returns a link to the file
        hosted on Discord using `get_hosted_file` method

        :param awmap: `AWMap` instance of map to export

        :return: `str` URL of hosted CSV file"""

        if awmap.title:
            title = awmap.title
        else:
            title = "Untitled"

        attachment = discord.File(
            fp=BytesIO(
                awmap.to_awbw.encode("utf-8")
            ),
            filename=f"{title}.csv"
        )
        url = await self.get_hosted_file(attachment)

        return url

    async def get_minimap(
            self,
            awmap: AWMap
    ) -> str:
        """Uses `AWMap`'s `minimap` parameter to generate a
        `PIL` image of a minimap representing the loaded map
        then returns a link to the file hosted on Discord
        using the `get_hosted_file` method

        :param awmap: `AWMap` instance of map

        :return: `str` URL of hosted minimap image"""

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

    """
        ######################################
        # Some Special Utilities for Discord #
        ######################################
    """

    def _color(self, channel) -> int:
        if isinstance(channel, discord.DMChannel):
            return 0
        else:
            return channel.guild.me.color.value

    def _inv(self, ctx: Context):
        return f"{ctx.prefix}{ctx.invoked_with}"

    """
        #####################
        # Formatting Embeds #
        #####################
    """

    def base_embed(self, channel, awmap: AWMap) -> discord.Embed:
        """Formats and returns the base embed with map
        title and author."""

        if awmap.awbw_id:
            a_url = f'http://awbw.amarriner.com/profile.php?username=' \
                    f'{quote(awmap.author)}'
            if awmap.author == "[Unknown]":
                author = "Design Map by [Unknown]"
            else:
                author = f"Design map by [{awmap.author}]({a_url})"
            m_url = f"http://awbw.amarriner.com/prevmaps.php?maps_id=" \
                    f"{awmap.awbw_id}"
        else:
            author = f"Design map by {awmap.author}"
            m_url = ""

        return discord.Embed(
            color=self._color(channel),
            title=awmap.title,
            description=author,
            url=m_url
        )

    async def em_load(self, channel, awmap: AWMap):
        """Formats and sends an embed to `channel` appropriate
        for when a map is loaded for a user."""

        em = self.base_embed(channel, awmap)

        image_url = await self.get_minimap(awmap)
        em.set_image(url=image_url)

        await channel.send(embed=em)

    async def em_download(self, channel, awmap: AWMap):
        """Formats and sends an embed to `channel` containing
        downloads for the supported map types."""

        em = self.base_embed(channel, awmap)

        aws = await self.get_aws(awmap)
        csv = await self.get_awbw(awmap)
        thumb = await self.get_minimap(awmap)

        em.add_field(
            name="Downloads",
            value=f"[AWS]({aws})\n[AWBW CSV]({csv})"
        )
        em.set_thumbnail(url=thumb)

        await channel.send(embed=em)

    """
        ###############################################
        # Administrative Commands for AdvanceWars cog #
        ###############################################
    """

    @checks.awbw_staff()
    @_map.command(name="listen", hidden=True, usage="[on / off]")
    async def listen(self, ctx: Context, *, arg: str=""):
        """Toggle active listening for maps

        With this option turned on, all messages
        will be checked for valid maps. Messages
        containing valid maps will be treated as
        a `[p]map load` command."""

        if arg.strip(" ").lower() in "on yes true y t".split(" "):
            self.db.set(f"{CONFIG}:listen_for_maps", True)
            self.listen_for_maps = True

        elif arg.strip(" ").lower() in "off no false n f".split(" "):
            self.db.set(f"{CONFIG}:listen_for_maps", False)
            self.listen_for_maps = False

        em = discord.Embed(
            color=self._color(ctx.channel),
            title="BattleMaps Config",
            description=f"Active Listen For Maps: `{self.listen_for_maps}`"
        )
        await ctx.send(embed=em)

    @checks.sudo()
    @_map.command(name="viewallmaps", hidden=True, aliases=["vam"])
    async def viewallmaps(self, ctx: Context):
        """View all currently loaded maps.

        Administrative command that will display
        Map titles and user IDs for all currently
        loaded maps"""
        em = discord.Embed(
            color=self._color(ctx.channel),
            title="All Currently Loaded Maps",
            description="\n".join(
                f"{k} @ {v['ts']}: {v['awmap'].title}"
                for k, v in self.loaded_maps.items()
            )
        )
        await ctx.send(embed=em)

    @checks.sudo()
    @_map.command(name="pull", hidden=True, aliases=["update"])
    async def _pull(self, ctx: Context):
        """Update the converter core

        Uses `pull` method to update AWSMapConvert
        and reload the cog."""
        if self.pull():
            await ctx.send("Converter core updated.\nReloading cog.")
            self.bot.remove_cog("AdvanceWars")
            self.bot.add_cog(AdvanceWars(self.bot))
        else:
            await ctx.send("Converter core already up-to-date.")

    @staticmethod
    def pull() -> bool:
        """Git Pull the AWSMapConverter. If it is not
        found, will Git Clone

        :returns bool: `True` if converter was updated
        successfully. `False` otherwise"""

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
            cmd = "git clone --no-pager" \
                  "https://github.com/SirThane/AWSMapConverter.git".split(" ")
            subprocess.run(cmd, **params)
            return True
        else:
            return True

    async def on_message(self, msg):
        if self.listen_for_maps and not msg.author.bot:
            if not msg.content.startswith(self.bot.command_prefix[0]):
                awmap = await CheckMap.check(msg, skips=["msg_csv", "id"])
                if awmap:
                    await self.em_load(msg.channel, awmap)
                    await self.timed_store(msg.author, awmap)


class CheckMap:

    @staticmethod
    async def check(
            msg: discord.Message,
            title: str="[Untitled]",
            skips: list=None
    ) -> Union[AWMap, None]:
        """Takes a discord.Message object and checks
        for valid maps that can be loaded.

        :param msg: `discord.Message` to check for maps
        :param title: Optional title for text maps
        :param skips: Optional list of checks to exclude

        :return: `AWMap` instance of valid map is found
        :return: `None` if no valid map is found"""

        if not skips:
            skips = ""

        if msg.attachments:
            attachment = msg.attachments[0]
            filename, ext = os.path.splitext(attachment.filename)

            if "aws" not in skips and ext == ".aws":
                return await CheckMap.from_aws(attachment)

            if "text" not in skips and ext.lower() in [".txt", ".csv"]:
                return await CheckMap.from_text(
                    attachment,
                    filename,
                    msg.author.mention
                )

        s_awl = RE_AWL.search(msg.content)

        if "link" not in skips and s_awl:
            return CheckMap.from_id(s_awl.group(3))

        s_csv = RE_CSV.search(msg.content)

        if s_csv:

            if "msg_csv" not in skips and 0 <= int(
                    s_csv.group(0).split(",")[0]) <= 176:
                return CheckMap.from_csv(
                    s_csv.group(0),
                    title,
                    msg.author.mention
                )

            if "id" not in skips:
                return CheckMap.from_id(s_csv.group(0))

        return

    @staticmethod
    async def from_aws(
            attachment: discord.Attachment
    ) -> Union[AWMap, None]:
        """Take an attachment with an 'AWS' extension
        and return an `AWMap` instance of the map data

        :param attachment: The `discord.Attachment`
        instance representing the attachment

        :return: `AWMap` instance with converted map data"""

        aws_bytes = BytesIO()

        try:
            await attachment.save(fp=aws_bytes)
            aws_bytes.seek(0)
            awmap = AWMap().from_aws(aws_bytes.read())
        except discord.HTTPException:
            raise errors.FileSaveFailureError
        else:
            return awmap

    @staticmethod
    async def from_text(
            attachment: discord.Attachment,
            filename: str,
            author: str
    ) -> Union[AWMap, None]:
        """Format an `AWMap` from a message attachment
        with "CSV" extension containing AWBW map
        data

        :param attachment: CSV text file of AWBW map data
        :param filename: Name portion of file name that
        will be used as Map title
        :param author: Map author name as a Discord mention

        :raises AWBWDimensionsError: if rows have differing
        number of columns

        :return: `AWMap` instance with map data"""

        awbw_bytes = BytesIO()
        await attachment.save(fp=awbw_bytes)
        awbw_bytes.seek(0)
        map_csv = awbw_bytes.read().decode("utf-8")

        try:
            awmap = AWMap().from_awbw(map_csv, title=filename)
            awmap.author = author
        except AssertionError:
            raise errors.AWBWDimensionsError
        else:
            return awmap

    @staticmethod
    def from_id(
            awbw_id: str
    ) -> Union[AWMap, None]:
        """Use `AWMap`'s `from_awbw` method to collect
        a map from AWBW using it's map ID

        :param awbw_id: ID of map on AWBW

        :raises InvalidMapError: if a Map with ID `awbw_id`
        is not found

        :return: `AWMap` instance with collected map data"""
        try:
            int(awbw_id)
            awmap = AWMap().from_awbw(awbw_id=awbw_id)
        except Exception:
            raise errors.InvalidMapError
        else:
            return awmap

    @staticmethod
    def from_csv(
            msg_csv: str,
            title: str,
            author: str
    ) -> Union[AWMap, None]:
        """Format an `AWMap` from a message containing raw
        AWBW CSV text

        :param msg_csv: CSV text of AWBW map data
        :param title: Map title
        :param author: Map author name as a Discord mention

        :raises AWBWDimensionsError: if rows have differing
        number of columns

        :return: `AWMap` instance with map data"""
        try:
            awmap = AWMap().from_awbw(data=msg_csv, title=title)
            awmap.author = author
        except AssertionError:
            raise errors.AWBWDimensionsError
        else:
            return awmap


def setup(bot):
    AdvanceWars.pull()
    bot.add_cog(AdvanceWars(bot))
