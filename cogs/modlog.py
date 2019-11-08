"""Fancy channel logs using rich embeds"""

from io import BytesIO

from asyncio import sleep
from datetime import datetime, timedelta
from discord import Colour, Embed, Guild, Member, Message, User
from discord.channel import DMChannel
from discord.enums import AuditLogAction, Enum
from discord.errors import Forbidden, HTTPException
from discord.ext.commands import Context, Cog, group
from discord.file import File
from pytz import timezone
from typing import List, Tuple, Union, Optional

from utils.classes import Bot
from utils.checks import sudo
from utils.utils import download_image, SubRedis


class EventColors(Enum):
    ban = Colour.dark_red()
    unban = Colour.teal()
    kick = Colour.red()
    join = Colour.dark_green()
    leave = Colour.blue()
    delete = Colour.magenta()
    edit = Colour.gold()
    name_change = Colour.purple()
    nickname_change = Colour.blurple()
    verified = Colour.light_grey()


class EventPriority(Enum):
    """Easy place to edit priority levels
    True = send to priority_modlog
    False = send to default_modlog
    To edit this behavior, edit ModLogs.log_event"""
    ban = True
    unban = True
    join = False
    leave = False
    kick = False
    delete = False
    edit = False
    update = False


class ModLogs(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.root_db = bot.db
        self.config = SubRedis(bot.db, f"{bot.APP_NAME}:modlog")

        self.errorlog = bot.errorlog

        # init a local cache of logged Guilds and their configs
        cache = dict()
        for key in self.config.scan_iter("guilds*"):
            *_, guild_id = key.split(":")
            try:
                cache[int(guild_id)] = self.config.hgetall(key)
            except TypeError:
                # Guild ID not found
                self.config.delete(key)

        self._config_cache = cache

    @property
    def active_guilds(self) -> List[int]:  # TODO: Use this
        return list(self._config_cache.keys())

    def _is_tracked(self, guild: Guild, priority_event: bool):
        """Perform a simple check before running each event so that we don't waste time trying to log"""
        if not guild:  # DMs
            return False
        elif guild.id not in self._config_cache.keys():
            return False
        elif priority_event and self._config_cache[guild.id].get("priority_modlog") is None:
            return False
        elif not priority_event and self._config_cache[guild.id].get("default_modlog") is None:
            return False
        else:
            return True

    def _create_guild_config(self, guild: Guild):
        config = {
            "priority_modlog": "None",
            "default_modlog": "None",
        }

        self.config.hmset(f"guilds:{guild.id}", config)
        self._config_cache[int(guild.id)] = config
        return config

    def get_guild_config(self, guild: Guild):
        """
        Get the guild's config, or create it if it doesn't exist.

        Expected format should be:
        {
            "priority_modlog": "id",
            "default_modlog": "id",
        }

        either modlog can be `None`, which just results in the event being discarded.
        :param guild: The tracked guild
        :return: guild config dict, or None if it doesn't exist
        """

        try:
            return self._config_cache.get(guild.id)
        except KeyError:
            # Let's just build it up anyway
            return self.config.hgetall(f"guilds:{guild.id}")

    @staticmethod
    def em_base(user: Union[Member, User], log_title: str, color: int) -> Embed:
        """Do basic formatting on the embed"""

        em = Embed(
            description=f"*{log_title}*",
            color=color
        )

        user_repr = f"{user.name}#{user.discriminator}   (ID: {user.id})"

        em.set_author(name=user_repr, icon_url=user.avatar_url)

        date, time = timezone("UTC").localize(datetime.now()).strftime("%b. %d, %Y#%I:%M UTC").split("#")
        em.set_footer(text=f"Event Timestamp: 📅 {date} || 🕒 {time}")

        return em

    async def log_event(self, embed: Embed, guild: Guild, priority: bool = False, **kwargs) -> None:
        """Have to use this backwards-ass method because it throws http exceptions."""

        guild_config = self.get_guild_config(guild)

        if priority:
            priority_modlog = int(guild_config.get("priority_modlog", 0))
            dest = self.bot.get_channel(priority_modlog)
        else:
            default_modlog = int(guild_config.get("default_modlog", 0))
            dest = self.bot.get_channel(default_modlog)

        if not dest:
            return

        try:
            await dest.send(embed=embed, **kwargs)
        except HTTPException as error:
            await self.errorlog.send(error)

    async def _get_last_audit_action(
            self,
            guild: Guild,
            action: int,
            member: Union[Member, User]
    ) -> Tuple[bool, bool, Optional[User], Optional[str]]:
        """Find the first Audit Log entry matching the action type.

        Will only search up to 10 log entries and only up to 5 seconds ago.

        Returns Tuple

        bool:           If log entry was found
        bool:           If exception is encountered (to adjust embed message)
        Optional[User]: The moderator that used moderation action or None
        Optional[str]:  The reason given for moderation action or None"""

        # Allow time so audit logs will be available
        await sleep(0.5)

        # Only search last 10 seconds of audit logs
        timeframe = datetime.utcnow() - timedelta(seconds=10.0)

        try:

            # Only search last 10 audit log entries
            # Action should be at the top of the stack
            for log_entry in await guild.audit_logs(action=action, limit=10, oldest_first=False).flatten():

                # after kwarg of Guild.audit_logs does not appear to work
                # Manually compare datetimes
                if log_entry.target.id == member.id and log_entry.created_at > timeframe:

                    # Get mod and reason
                    # Should always get mod
                    # Reason is optional
                    mod = getattr(log_entry, "user", None)
                    reason = getattr(log_entry, "reason", None)

                    return True, False, mod, reason

            # Could not find audit log entry
            # member_remove was voluntary leave
            else:
                return False, False, None, None

        # Do not have access to audit logs
        except Forbidden as error:
            print(error)
            return False, True, None, None

        # Catch any unknown errors and log them
        # We need this method to return so event still logs
        except Exception as error:
            await self.errorlog.send(error)
            return False, True, None, None

    """ ###################
         Registered Events
        ################### """

    @Cog.listener(name="on_member_ban")
    async def on_member_ban(self, guild: Guild, user: Union[Member, User], *args):
        """Event called when a user is banned.
        User does not need to currently be a member to be banned."""

        if not self._is_tracked(guild, EventPriority.ban):
            return

        # Event is sometimes called with 3 arguments
        # Capture occurrence
        await self.errorlog.send(Exception(f"Additional arguments sent to `on_member_ban`: {args}"))

        em = self.em_base(
            user,
            f"User {user.mention} ({user.name}) was banned",
            EventColors.ban.value
        )

        # Attempt to retrieve unban reason and mod that unbanned from Audit Log
        found, errored, mod, reason = await self._get_last_audit_action(guild, AuditLogAction.ban, user)

        # Audit log action found
        # Add details
        if found and not errored:
            em.add_field(
                name="Banned By",
                value=f"{mod.mention}\n({mod.name}#{mod.discriminator})"
            )
            em.add_field(
                name="Reason",
                value=reason if reason is not None else "No reason given"
            )

        # Cannot access audit log or HTTP error prevented access
        elif errored and not found:
            em.add_field(
                name="Banned By",
                value="Unknown\nAudit Log inaccessible"
            )
            em.add_field(
                name="Reason",
                value="Irretrievable\nAudit Log inaccessible"
            )

        # No audit log entry found for ban
        else:
            em.add_field(
                name="Banned By",
                value="Unknown\nAudit Log missing data"
            )
            em.add_field(
                name="Reason",
                value="Irretrievable\nAudit Log missing data or no reason given"
            )

        # If banned user was a member of the server, capture roles
        if isinstance(user, Member):
            roles = "\n".join([role.mention for role in sorted(user.roles, reverse=True) if role.name != "@everyone"])
            em.add_field(
                name="Roles",
                value=roles if roles else "User had no roles"
            )

        await self.log_event(em, guild, priority=EventPriority.ban)

    @Cog.listener(name="on_member_unban")
    async def on_member_unban(self, guild: Guild, user: User, *args):
        """Event called when a user is unbanned"""

        if not self._is_tracked(guild, EventPriority.unban):
            return

        # Event is sometimes called with 3 arguments
        # Capture occurrence
        await self.errorlog.send(Exception(f"Additional arguments sent to `on_member_unban`: {args}"))

        em = self.em_base(
            user,
            f"User {user.mention} ({user.name}) was unbanned",
            EventColors.unban.value
        )

        # Attempt to retrieve unban reason and mod that unbanned from Audit Log
        found, errored, mod, reason = await self._get_last_audit_action(guild, AuditLogAction.unban, user)

        # Audit log action found
        # Add details
        if found and not errored:
            em.add_field(
                name="Unbanned By",
                value=f"{mod.mention}\n({mod.name}#{mod.discriminator})"
            )
            em.add_field(
                name="Reason",
                value=reason if reason is not None else "No reason given"
            )

        # Cannot access audit log or HTTP error prevented access
        elif errored and not found:
            em.add_field(
                name="Unbanned By",
                value="Unknown\nAudit Log inaccessible"
            )
            em.add_field(
                name="Reason",
                value="Irretrievable\nAudit Log inaccessible"
            )

        # No audit log entry found for ban
        else:
            em.add_field(
                name="Unbanned By",
                value="Unknown\nAudit Log missing data"
            )
            em.add_field(
                name="Reason",
                value="Irretrievable\nAudit Log missing data or no reason given"
            )

        await self.log_event(em, guild, priority=EventPriority.unban)

    @Cog.listener(name="on_member_join")
    async def on_member_join(self, member: Member):
        """Event called when a member joins the guild"""

        if not self._is_tracked(member.guild, EventPriority.join):
            return

        em = self.em_base(
            member,
            f"User {member.mention} ({member.name}) joined",
            EventColors.join.value
        )

        date, time = timezone("UTC").localize(member.created_at).strftime("%b. %d, %Y#%I:%M UTC").split("#")

        em.add_field(
            name="Account Creation Timestamp",
            value=f"📅 {date} || 🕒 {time}"
        )

        await self.log_event(em, member.guild, priority=EventPriority.join)

    @Cog.listener(name="on_member_remove")
    async def on_member_remove(self, member: Member):
        """Event called when a member is removed from the guild

        This event will be called if the member leaves, is kicked, or is banned"""

        if not self._is_tracked(member.guild, EventPriority.leave):
            return

        # Stop if ban. Will be handled in on_member_ban
        found, *_ = await self._get_last_audit_action(member.guild, AuditLogAction.ban, member)
        if found:
            return

        # Attempt to retrieve kic reason and mod that kicked from Audit Log
        found, errored, mod, reason = await self._get_last_audit_action(member.guild, AuditLogAction.kick, member)

        # Kick found in audit log
        if found and not errored:
            leave_type = EventPriority.kick

            em = self.em_base(
                member,
                f"User {member.mention} ({member.name}) was kicked",
                EventColors.kick.value
            )

            em.add_field(
                name="Kicked By",
                value=f"{mod.mention}\n({mod.name}#{mod.discriminator})"
            )

            em.add_field(
                name="Reason",
                value=reason if reason else "No reason given"
            )

        # Cannot access audit log or HTTP error prevented access
        elif errored and not found:
            print("errored and not found")
            leave_type = EventPriority.kick
            em = self.em_base(
                member,
                f"User {member.name} may have been kicked",
                EventColors.kick.value
            )
            em.description = f"{em.description}\n\nAudit Log inaccessible\n" \
                             f"Unable to determine if member remove was kick or leave"
            em.add_field(
                name="Kicked By",
                value="Unknown\nAudit Log inaccessible"
            )
            em.add_field(
                name="Reason",
                value="Irretrievable\nAudit Log inaccessible"
            )

        # Successfully accessed audit log and found no kick
        # Presume voluntary leave
        else:
            leave_type = EventPriority.leave

            em = self.em_base(
                member,
                f"User {member.mention} ({member.name}) left",
                EventColors.kick.value
            )

        roles = "\n".join([role.mention for role in sorted(member.roles, reverse=True) if role.name != "@everyone"])
        em.add_field(
            name="Roles",
            value=roles if roles else "User had no roles"
        )

        await self.log_event(em, member.guild, priority=leave_type)

    # @Cog.listener(name="on_member_remove")
    # async def on_member_remove(self, member: Member):
    #     if not self._is_tracked(member.guild, EventPriority.leave):
    #         return
    #
    #     # We need to check to see if it was a ban, which also triggers the member_remove handle
    #     leave_type = EventPriority.leave
    #
    #     await sleep(1)
    #
    #     # Check to see if the leave was a kick or just a regular leave
    #     try:
    #         for log_entry in await member.guild.audit_logs(action=AuditLogAction.kick, limit=1).flatten():
    #
    #             # Let's stop at the first entry.
    #             if log_entry.target.id == member.id:  # The leave was a kick
    #                 leave_type = EventPriority.kick
    #
    #                 try:
    #                     mod_responsible = getattr(log_entry, "user", "Unknown")
    #                     reason = getattr(log_entry, "reason", "No reason provided.")
    #
    #                     em = Embed(
    #                         title=f"User {member} was kicked.",
    #                         color=EventColors.kick.value
    #                     )
    #                     em.add_field(name="Reason", value=reason)
    #                     em.add_field(name="Kicked by", value=mod_responsible)
    #                     break
    #
    #                 except AttributeError:
    #                     pass
    #
    #         else:
    #             em = Embed(
    #                 title=f"User {member} left.",
    #                 color=EventColors.leave.value
    #             )
    #
    #     except Forbidden:
    #         mod_log_channel_id = self.get_guild_config(member.guild)["default_modlog"]
    #         modlog_chan = self.bot.get_channel(int(mod_log_channel_id))
    #         await modlog_chan.send("I'm missing audit log permissions, so ban and kick tracking won't work.")
    #         return
    #
    #     em = self.em_base(em, member)
    #     roles = ", ".join((i.name for i in member.roles))
    #     em.add_field(name="Roles", value=roles)
    #
    #     await self.log_event(em, member.guild, priority=leave_type)

    @Cog.listener(name="on_message_delete")
    async def on_message_delete(self, msg: Message):
        """Event called when a message is deleted"""

        if not self._is_tracked(msg.guild, EventPriority.delete):
            return

        # if msg.author.id == self.bot.user.id:
        #     return

        reupload = None
        member = msg.author

        em = self.em_base(
            member,
            f"Message by {member.mention} ({member.name}) deleted",
            EventColors.delete.value
        )

        em.description = f"{em.description}\n\nChannel: {msg.channel.mention} ({msg.channel.name})"

        if msg.content:
            chunks = [msg.content[i:i + 1024] for i in range(0, len(msg.content), 1024)]
            for i, chunk in enumerate(chunks):
                em.add_field(
                    name=f"Content [{i + 1}/{len(chunks)}]",
                    value=chunk
                )

        # Try to re-download attached images if possible.
        # The proxy url doesn't 404 immediately unlike the regular URL, so it may be possible to download from it
        # before it goes down as well.

        if msg.attachments:
            temp_image = BytesIO()
            attachment = msg.attachments[0]
            if attachment.size > 5000000:
                # caching is important and all, but this will just cause more harm than good
                return

            try:
                await download_image(msg.attachments[0].proxy_url, temp_image)
                reupload = File(temp_image, filename="reupload.{}".format(attachment.filename))

                em.description = f"{em.description}\n\n**Attachment Included Above**"

            except Exception as error:
                await self.errorlog.send(error)
                reupload = None

                em.description = f"{em.description}\n\n**Attachment Reupload Failed (See Error Log)**"

        await self.log_event(em, msg.guild, priority=EventPriority.delete, file=reupload)

    @Cog.listener(name="on_message_edit")
    async def on_message_edit(self, before: Message, after: Message):
        """Event called when a message is edited"""
        if not self._is_tracked(before.guild, EventPriority.edit):
            return

        if before.author.id == self.bot.user.id:
            return

        if before.content == after.content or isinstance(before.channel, DMChannel):
            return

        em = self.em_base(
            before.author,
            f"Message by {before.author.mention} ({before.author.name}) edited",
            EventColors.edit.value
        )

        em.description = f"{em.description}\n\nChannel: {before.channel.mention} ({before.channel.name})"

        if before.content:
            chunks = [before.content[i:i + 1024] for i in range(0, len(before.content), 1024)]
            for i, chunk in enumerate(chunks):
                em.add_field(
                    name=f"Before [{i + 1}/{len(chunks)}]",
                    value=chunk
                )
        else:
            em.add_field(
                name="Before [0/0]",
                value="Message had no content"
            )
        if after.content:
            chunks = [after.content[i:i + 1024] for i in range(0, len(after.content), 1024)]
            for i, chunk in enumerate(chunks):
                em.add_field(
                    name=f"After [{i + 1}/{len(chunks)}]",
                    value=chunk
                )

        await self.log_event(em, before.guild, priority=EventPriority.edit)

    @Cog.listener(name="on_member_update")
    async def on_member_update(self, before: Member, after: Member):
        """Event called when a user's member profile is changed"""

        if not self._is_tracked(before.guild, EventPriority.update):
            return

        if before.name != after.name:
            em = self.em_base(
                after,
                f"Member {before.mention} ({before.name}) changed their name to {after.name}",
                EventColors.name_change.value
            )

            await self.log_event(em, before.guild, priority=EventPriority.update)

        if before.nick != after.nick:

            if after.nick is None:
                em = self.em_base(
                    after,
                    f"Member {before.mention} ({before.name}) reset their nickname",
                    EventColors.nickname_change.value
                )

            else:
                em = self.em_base(
                    after,
                    f"Member {before.mention} ({before.name}) changed their nickname to {after.nick}",
                    EventColors.nickname_change.value
                )

            await self.log_event(em, after.guild, priority=EventPriority.update)

    """ ##########
         Commands
        ########## """

    @sudo()
    @group(name="modlog", invoke_without_command=True)
    async def modlog(self, ctx: Context):  # TODO: List enabled guilds with their channels
        pass

    @sudo()
    @modlog.command(name="enable")
    async def enable(self, ctx: Context, *, guild: int = None):
        """Enable logging on a Guild

        You must also set default and/or priority log channels
        with `[p]modlog set (default/priority)`"""

        if guild is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild)

        if not guild:
            return await ctx.message.add_reaction("⚠")

        self._create_guild_config(guild)

        await ctx.message.add_reaction("✅")

    @sudo()
    @modlog.command(name="disable")
    async def disable(self, ctx: Context, guild: int = None):
        """Disable logging on a Guild

        Guild and its config will be removed from the database"""

        if guild is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild)

        if not guild:
            return await ctx.message.add_reaction("⚠")

        if guild.id not in self.active_guilds:
            return await ctx.message.add_reaction("⚠")

        self._config_cache.pop(guild.id)
        self.config.delete(f"guilds:{guild.id}")

        await ctx.message.add_reaction("✅")

    @sudo()
    @modlog.group(name="set", invoke_without_command=True)
    async def _set(self, ctx: Context):  # TODO: Show guilds and configs?
        pass

    @sudo()
    @_set.command(name="default")
    async def default(self, ctx: Context, *, guild: int = None, channel: int = None):
        """Set modlog Channel for "default" messages

        `guild` must be a tracked Guild
        `channel` does not necessarily need to be a Channel in `guild`"""

        if not guild:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild)
        if not guild:
            return await ctx.message.add_reaction("⚠")

        if guild.id not in self.active_guilds:
            return await ctx.message.add_reaction("⚠")

        if not channel:
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(channel)
        if not channel:
            return await ctx.message.add_reaction("⚠")

        config = self.get_guild_config(guild)
        config["default_modlog"] = str(channel.id)

        self.config.hmset(f"guilds:{guild.id}", config)
        self._config_cache[guild.id] = config

        await ctx.message.add_reaction("✅")

    @sudo()
    @_set.command(name="priority")
    async def priority(self, ctx: Context, *, guild: int = None, channel: int = None):
        """Set modlog channel for "priority" messages

        `guild` must be a tracked Guild
        `channel` does not necessarily need to be a Channel in `guild`"""

        if not guild:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild)
        if not guild:
            return await ctx.message.add_reaction("⚠")

        if guild.id not in self.active_guilds:
            return await ctx.message.add_reaction("⚠")

        if not channel:
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(channel)
        if not channel:
            return await ctx.message.add_reaction("⚠")

        config = self.get_guild_config(guild)
        config["priority_modlog"] = str(channel.id)

        self.config.hmset(f"guilds:{guild.id}", config)
        self._config_cache[guild.id] = config

        await ctx.message.add_reaction("✅")


def setup(bot: Bot):
    bot.add_cog(ModLogs(bot))
