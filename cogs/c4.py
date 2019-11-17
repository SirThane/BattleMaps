"""Connect Four
Written for Python 3.6 and discord.py 1.0.0a"""

from random import choice

from asyncio import sleep
from discord.channel import TextChannel
from discord.colour import Colour
from discord.embeds import Embed
from discord.enums import Enum
from discord.ext.commands import group
from discord.ext.commands.converter import MemberConverter
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.errors import BadArgument, NoPrivateMessage
from discord.member import Member
from discord.message import Message
from discord.reaction import Reaction
from discord.role import Role
from discord.user import User
from typing import Union, Optional, List, Tuple

from utils.checks import sudo
from utils.classes import Bot
from utils.utils import SubRedis


class Emoji(Enum):
    white = b'\xE2\x9A\xAA'.decode("utf8")      # :white_circle:        ⚪
    red = b'\xF0\x9F\x94\xB4'.decode("utf8")    # :red_circle:          🔴
    blue = b'\xF0\x9F\x94\xB5'.decode("utf8")   # :large_blue_circle:   🔵
    vs = b'\xF0\x9F\x86\x9A'.decode("utf8")     # :vs:                  🆚
    tada = b'\xF0\x9F\x8E\x89'.decode("utf8")   # :tada:                🎉
    one = b'\x31\xE2\x83\xA3'.decode("utf8")    # :one:                 1⃣
    two = b'\x32\xE2\x83\xA3'.decode("utf8")    # :two:                 2⃣
    three = b'\x33\xE2\x83\xA3'.decode("utf8")  # :three:               3⃣
    four = b'\x34\xE2\x83\xA3'.decode("utf8")   # :four:                4⃣
    five = b'\x35\xE2\x83\xA3'.decode("utf8")   # :five:                5⃣
    six = b'\x36\xE2\x83\xA3'.decode("utf8")    # :six:                 6⃣
    seven = b'\x37\xE2\x83\xA3'.decode("utf8")  # :seven:               7⃣
    x = b'\xE2\x9D\x8C'.decode("utf8")          # :x:                   ❌
    info = b'\xE2\x84\xB9'.decode("utf8")       # :information_source:  ℹ
    warning = b'\xE2\x9A\xA0'.decode("utf8")    # :warning:             ⚠
    error = b'\xe2\x9b\x94'.decode("utf8")      # :no_entry:            ⛔

    def __str__(self):
        return self.value


class State(Enum):
    init = -1
    active = 0
    won = 1
    draw = 2
    forfeit = 3
    timeout = 4


class MsgLevel(Enum):
    info = 0
    warning = 1
    error = 2


MSG_ICON = [Emoji.info, Emoji.warning, Emoji.error]


MSG_COLOR = [Colour.blue(), Colour.orange(), Colour.red()]


AWBW_ROLES = {
    "os": 424524133670453250,  # Orange Star Commander
    "bm": 424524139999789058,  # Blue Moon Commander
    "ge": 424524144353476629,  # Green Earth Commander
    "yc": 424524148958560266,  # Yellow Comet Commander
    "bh": 424524153387876353,  # Black Hole Commander
    "rf": 424541540740890624,  # Red Fire Commander
    "gs": 424541543810990089,  # Grey Sky Commander
    "bd": 424541547757961216,  # Brown Desert Commander
    "ab": 424541550853488640,  # Amber Blaze Commander
    "js": 424541553898291200,  # Jade Sun Commander
    "ci": 424541559766122518,  # Cobalt Ice Commander
    "pc": 424541563520024576,  # Pink Cosmos Commander
    "tg": 424541566934319104,  # Teal Galaxy Commander
    "pl": 424541571300589587,  # Purple Lightning Commander
    "ar": 455439202692366367,  # Acid Rain Commander
    "wn": 455439210883842048,  # White Nova Commander
}


AWBW_EMOJIS = {
    "ne": "<:00nepcity:642860586627104793>",
    "os": "<:01ospcity:645389334656057374>",
    "bm": "<:02bmpcity:645389346949693451>",
    "ge": "<:03gepcity:645389367212244999>",
    "yc": "<:04ycpcity:645389390046298112>",
    "bh": "<:05bhpcity:645389406978441237>",
    "rf": "<:06rfpcity:645389422455554069>",
    "gs": "<:07gspcity:645389441468465188>",
    "bd": "<:08bdpcity:645389453585678337>",
    "ab": "<:09abpcity:645389480806711337>",
    "js": "<:10jspcity:645389506849013773>",
    "ci": "<:11cipcity:645389550054801428>",
    "pc": "<:12pcpcity:645389568895483941>",
    "tg": "<:13tgpcity:645389594522550273>",
    "pl": "<:14plpcity:645389637719818261>",
    "ar": "<:15arpcity:645389659152580802>",
    "wn": "<:16wnpcity:645389705772400642>",
}


class Player:
    """Board Game Participant"""
    def __init__(self, member: Member, chip: str):
        self.member = member

        # String that represents the player's chip
        self.chip = chip

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """Returns the username of the Member representing player"""
        return self.member.name

    @property
    def color(self) -> int:
        """Returns the integer Colour value of the Member representing Player"""
        return self.member.color

    @property
    def id(self) -> int:
        """Returns the User ID of the Member representing Player"""
        return self.member.id

    @property
    def default_avatar(self) -> str:
        """Returns name of default avatar for Member"""
        return self.member.default_avatar.name


class ConnectFourSession:
    """Active Session of Connect Four"""

    def __init__(
            self,
            p1: Member,
            p2: Member,
            p1_chip: str = Emoji.red,
            p2_chip: str = Emoji.blue,
            empty: str = Emoji.white
    ):

        # Instantiate the players
        self.p1 = Player(p1, p1_chip)
        self.p2 = Player(p2, p2_chip)

        # Put players in a dict for helper methods
        self.players = {
            self.p1.id: self.p1,
            self.p2.id: self.p2
        }

        # Empty space
        self.empty = empty

        # Set up empty board and
        self.piece_count = {i + 1: 0 for i in range(7)}
        self.board = {x + 1: {y + 1: 0 for y in range(6)} for x in range(7)}

        self.turn = 0
        self.timeout = 0

        # New games are in `init` state
        self.state = State.init

        self.msg = None

    def __str__(self):
        return f"{self.p1.name} v {self.p2.name} | " \
               f"Turn: {(self.turn + 2) // 2} | " \
               f"Current: {self.current_player.name}"

    """ ####################
         Player Information
        #################### """

    @property
    def current_player(self) -> Player:
        """
        :return: Instance of Player for current player
        """
        return self.p1 if self.turn % 2 == 0 else self.p2

    @property
    def current_player_chip(self) -> str:
        """
        :return: Emoji corresponding to current player's piece
        """
        return self.current_player.chip

    """ ###########################################
         Preparing Information For Discord Message
        ########################################### """

    @property
    def colour(self) -> int:
        """
        :return: attr of Colour for player's default avatar
        """
        name = self.current_player.default_avatar
        if name == "grey":
            name = "light_grey"
        return getattr(Colour, name)()

    @property
    def draw_board(self) -> str:
        """
        :return: String representation of current board using Emojis for pieces
        """
        board = list()
        for row in list(self.board.values()):
            board.append([getattr(player, "chip", self.empty) for player in row.values()])

        return "\n".join(["{}{}{}{}{}{}{}".format(*[board[x][y] for x in range(7)]) for y in range(6)][::-1])

    """ #################################
         Methods For Checking Game State
        ################################# """

    @property
    def valid_moves(self) -> List[int]:
        """
        :return: List of columns that are not full
        """
        return [column for column in self.board.keys() if self.piece_count[column] < 6]

    def check(self) -> None:
        """
        :return: Instance of Player for player if win condition detected,
        else, "Draw" if board full without win, else, None
        """

        # Check all vertical win conditions
        for x in range(1, 8):
            for y in range(1, 4):
                if getattr(self.board[x][y], "id", None):
                    if all([self.board[x][y] == self.board[x][y + i] for i in range(1, 4)]):
                        self.state = State.won
                        return

        # Check all horizontal win conditions
        for x in range(1, 5):
            for y in range(1, 7):
                if getattr(self.board[x][y], "id", None):
                    if all([self.board[x][y] == self.board[x + i][y] for i in range(1, 4)]):
                        self.state = State.won
                        return

        # Check all forward diagonal win conditions
        for x in range(1, 5):
            for y in range(1, 4):
                if getattr(self.board[x][y], "id", None):
                    if all([self.board[x][y] == self.board[x + i][y + i] for i in range(1, 4)]):
                        self.state = State.won
                        return

        # Check all backward diagonal win conditions
        for x in range(4, 8):
            for y in range(1, 4):
                if getattr(self.board[x][y], "id", None):
                    if all([self.board[x][y] == self.board[x - i][y + i] for i in range(1, 4)]):
                        self.state = State.won
                        return

        # If top-most slot is filled in all columns with no winner, Draw game
        if all(map(lambda space: isinstance(space, Player), [column[6] for column in self.board.values()])):
            self.state = State.draw
            return

    """ #####################
         Methods For Playing
        ##################### """

    def play(self, player: Member, column: int) -> None:
        """
        :param player: Member making a move
        :param column: Column played
        :return: Player if game is ended
        """

        self.state = State.active

        if column not in self.valid_moves:
            raise ValueError(f"Column {column} is full")

        # Increment piece count for column and put player in that slot
        self.piece_count[column] += 1
        self.board[column][self.piece_count[column]] = self.players.get(player.id)

        # Check for game over conditions
        self.check()

        # Return the player instance if the game is no longer active
        if self.state != State.active:
            return

        # Increment the turn counter and reset the timer for still active game
        self.turn += 1
        self.timeout = 0

    def forfeit(self):
        """Ends game by voluntary forfeit with player as loser"""
        self.state = State.forfeit

    def expire(self):
        """Ends the game by timeout with current player as loser"""
        self.state = State.timeout


class ConnectFour(Cog):
    """Play a game of Connect Four

    See `[p]help c4` manual for individual
    commands for more information.

    The classic game of Connect Four.
    Use these commands to play a game
    of Connect Four with another user.
    You can have multiple concurrent
    games, one per channel."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.root_db = bot.db
        self.config = SubRedis(bot.db, f"{bot.APP_NAME}:c4")

        self.sessions = dict()
        self.timeout = 120
        self.timeout_incr = 1

        # Valid reactions
        self._game_reactions = [
            str(Emoji.one),
            str(Emoji.two),
            str(Emoji.three),
            str(Emoji.four),
            str(Emoji.five),
            str(Emoji.six),
            str(Emoji.seven),
            str(Emoji.x)
        ]

        # Default chips
        self.empty_chip = AWBW_EMOJIS["ne"]
        self.p1_chip = AWBW_EMOJIS["os"]
        self.p2_chip = AWBW_EMOJIS["bm"]

    def session(self, channel: TextChannel) -> Optional[ConnectFourSession]:
        """Returns an active ConnectFourSession if there is a running game in a channel"""
        return self.sessions.get(channel.id, None)

    def channel_check(self, channel: TextChannel) -> bool:
        """Returns true if C4 is enabled in channel"""
        return str(channel.id) in self.config.smembers("allowed_channels")

    @staticmethod
    async def member_check(ctx: Context, member: str) -> Optional[Member]:
        """Attempt to convert an argument an argument to :class:`Member`"""
        try:
            return await MemberConverter().convert(ctx, member)
        except (BadArgument, NoPrivateMessage, TypeError):
            return None

    @staticmethod
    def get_member_chip(roles: List[Role], skip: str = None) -> Tuple[str, str]:
        for ctry, role_id in AWBW_ROLES.items():
            if role_id in [r.id for r in roles] and ctry != skip:
                return ctry, AWBW_EMOJIS[ctry]
        else:
            ctry = choice([ctry for ctry in AWBW_EMOJIS.keys() if ctry != skip])
            return ctry, AWBW_EMOJIS[ctry]

    @staticmethod
    async def send_message(channel: TextChannel, msg: str = "Error", level: int = MsgLevel.info) -> None:
        """Formats a message as embed"""

        em = Embed(
            description=f"{MSG_ICON[level.value]}  {msg}",
            color=MSG_COLOR[level.value]
        )
        msg = await channel.send(embed=em)
        await sleep(5)
        await msg.delete()

    async def init_game_message(self, channel: TextChannel, session: ConnectFourSession, board: Embed) -> Message:
        """Sends game board to channel and sets message on session"""

        msg = await channel.send(embed=board)

        for react in self._game_reactions:
            await msg.add_reaction(str(react))
            await sleep(0.1)

        session.msg = msg

        return msg

    async def send_board(self, channel: TextChannel) -> Message:
        """Prepare game Embed and update message"""

        session = self.session(channel)

        em = Embed(
            title=f"{session.p1.chip}{session.p1.name} {Emoji.vs} {session.p2.name}{session.p2.chip}",
            description=f"\n"
                        f"{Emoji.one}{Emoji.two}{Emoji.three}{Emoji.four}{Emoji.five}{Emoji.six}{Emoji.seven}\n"
                        f"{session.draw_board}"
        )

        if session.state == State.init:
            em.description = f"New game! Turn: 1\n" \
                             f"{em.description}\n" \
                             f"\n" \
                             f"{session.current_player.name}'s turn: {session.current_player.chip}"
            em.colour = session.colour

            return await self.init_game_message(channel, session, em)

        elif session.state == State.active:
            em.description = f"Turn: {(session.turn + 2) // 2}\n" \
                             f"{em.description}\n" \
                             f"\n" \
                             f"{session.current_player.name}'s turn: {session.current_player.chip}"
            em.colour = session.colour

        elif session.state == State.draw:
            self.sessions.pop(channel.id)
            em.description = f"Game ended in a Draw.\n" \
                             f"{em.description}"
            em.colour = Colour.dark_grey()
            await session.msg.clear_reactions()

        elif session.state == State.forfeit:
            self.sessions.pop(channel.id)
            em.description = f"Game Over. {session.current_player.name} Forfeits.\n" \
                             f"{em.description}"
            em.colour = Colour.dark_grey()
            await session.msg.clear_reactions()

        elif session.state == State.timeout:
            self.sessions.pop(channel.id)
            em.description = f"Time Out. {session.current_player.name} Forfeits.\n" \
                             f"{em.description}"
            em.colour = Colour.dark_grey()
            await session.msg.clear_reactions()

        elif session.state == State.won:
            self.sessions.pop(channel.id)
            em.description = f"Game Over!\n{session.current_player.name} wins! {Emoji.tada}\n" \
                             f"{em.description}"
            em.colour = 0xFDFF00
            await session.msg.clear_reactions()

        # TODO: check I can edit the message (retrievable), if not, init message
        return await session.msg.edit(embed=em)

    @group(name="c4", invoke_without_command=True)
    async def c4(self, ctx: Context, *, member: Member = None):
        """Connect Four

        `[p]c4 @user` to start a game with
        another user in the current channel."""

        if not self.channel_check(ctx.channel):
            return await self.send_message(
                ctx.channel,
                msg="Connect Four is not enabled in this channel",
                level=MsgLevel.error
            )

        elif not member:
            return await self.bot.help_command.send_help_for(ctx, ctx.command, "You need another player to start")

        elif member.id == ctx.author.id:
            return await self.send_message(
                ctx.channel,
                msg="You cannot start a game with yourself.",
                level=MsgLevel.warning
            )

        elif member.bot:
            return await self.send_message(
                ctx.channel,
                msg="You cannot play against bots ~~(yet <:doritoface:337530039677485057>)~~",
                level=MsgLevel.warning
            )

        elif member.id == ctx.author.id:
            return await self.send_message(
                ctx.channel,
                msg="You cannot start a game with yourself.",
                level=MsgLevel.warning
            )

        else:
            p2_ctry, p2_chip = self.get_member_chip(ctx.author.roles)
            _, p1_chip = self.get_member_chip(member.roles, p2_ctry)

            self.sessions[ctx.channel.id] = ConnectFourSession(
                p1=member,
                p1_chip=p1_chip,
                p2=ctx.author,
                p2_chip=p2_chip,
                empty=self.empty_chip
            )
            await self.send_board(ctx.channel)

    @c4.command(name="help", hidden=True)
    async def _help(self, ctx):
        """Shortcut to send help manual for ConnectFour"""
        await self.bot.help_command.send_help_for(ctx, self.bot.get_cog("ConnectFour"))

    @sudo()
    @c4.command(name="enable", hidden=True)
    async def c4_enable(self, ctx: Context, *, chan: TextChannel = None):
        """Enable Connect Four on a channel

        Run without an argument to enable on the current channel
        Pass a channel as an argument to enable on that channel"""

        if not chan:
            chan = ctx.channel

        if self.config.sadd("allowed_channels", chan.id):
            await self.send_message(
                ctx.channel,
                msg="Connect Four successfully enabled on channel.",
                level=MsgLevel.info
            )

        else:
            await self.send_message(
                ctx.channel,
                msg="Connect Four already enabled on channel.",
                level=MsgLevel.warning
            )

    @sudo()
    @c4.command(name="disable", hidden=True)
    async def c4_disable(self, ctx: Context, *, chan: TextChannel = None):
        """Disable Connect Four on a channel

        Run without an argument to disabled on the current channel
        Pass a channel as an argument to disable on that channel"""

        if not chan:
            chan = ctx.channel

        if self.config.srem("allowed_channels", chan.id):
            await self.send_message(
                ctx.channel,
                msg="Connect Four successfully disabled on channel.",
                level=MsgLevel.info
            )

        else:
            await self.send_message(
                ctx.channel,
                msg="Connect Four already disabled on channel.",
                level=MsgLevel.warning
            )

    @sudo()
    @c4.command(name="games", hidden=True)
    async def c4_games(self, ctx: Context):
        """Shows the number of running sessions"""
        sessions = '\n'.join([str(s) for s in self.sessions.values()])
        await self.send_message(
            ctx.channel,
            msg=f"Total running games: {len(self.sessions.keys())}\n"
                f"\n"
                f"{sessions}",
            level=MsgLevel.info
        )

    @sudo()
    @c4.command(name="kill", hidden=True)
    async def c4_kill(self, ctx: Context, *, _all: bool = False):
        """Administrative kill command

        This will kill a running game in the current channel"""
        if not _all:
            if self.sessions.pop(ctx.channel.id, None):
                await self.send_message(
                    ctx.channel,
                    msg="Current game in this channel has been terminated.",
                    level=MsgLevel.info
                )
            else:
                await self.send_message(
                    ctx.channel,
                    msg="No active game in this channel.",
                    level=MsgLevel.warning
                )
        else:
            await self.send_message(
                ctx.channel,
                msg=f"All running games have been terminated. (Total: {len(self.sessions.keys())})",
                level=MsgLevel.info
            )
            self.sessions = dict()

    @sudo()
    @c4.command(name="killall", hidden=True)
    async def c4_killall(self, ctx: Context):
        """Administrative kill command

        This will kill all running games in all channels"""

        ctx.message.content = f"{self.bot.command_prefix}kill True"
        await self.bot.process_commands(ctx.message)

    @Cog.listener(name="on_reaction_add")
    async def on_reaction_add(self, reaction: Reaction, user: Union[User, Member]):

        await sleep(0.1)

        if not self.channel_check(reaction.message.channel):
            # Channel is not watched for Connect Four
            return

        if user.id == self.bot.user.id:
            # Ignore the bot's own reactions
            return

        # It's a watched channel, so try to get an active session
        session = self.session(reaction.message.channel)

        if not session:
            # No session in channel
            return

        if reaction.message.id != session.msg.id:
            # Message is not an active session
            return

        if reaction.emoji not in self._game_reactions:
            # Not a valid game reaction
            return

        # It is a valid game reaction on an active session in a watched channel
        # Remove reaction, then act based on reaction
        await reaction.remove(user)

        if user.id not in session.players:
            # Not a player
            return

        if user.id != session.current_player.id:
            # Not the player's turn
            await self.send_message(
                reaction.message.channel,
                msg=f"{user.mention}: It is not your turn.",
                level=MsgLevel.warning
            )
            return

        if reaction.emoji == str(Emoji.one):
            try:
                session.play(user, 1)
            except ValueError:
                await self.send_message(
                    reaction.message.channel,
                    msg="That column is full. Select another.",
                    level=MsgLevel.error
                )
            return await self.send_board(reaction.message.channel)

        if reaction.emoji == str(Emoji.two):
            try:
                session.play(user, 2)
            except ValueError:
                await self.send_message(
                    reaction.message.channel,
                    msg="That column is full. Select another.",
                    level=MsgLevel.error
                )
            return await self.send_board(reaction.message.channel)

        if reaction.emoji == str(Emoji.three):
            try:
                session.play(user, 3)
            except ValueError:
                await self.send_message(
                    reaction.message.channel,
                    msg="That column is full. Select another.",
                    level=MsgLevel.error
                )
            return await self.send_board(reaction.message.channel)

        if reaction.emoji == str(Emoji.four):
            try:
                session.play(user, 4)
            except ValueError:
                await self.send_message(
                    reaction.message.channel,
                    msg="That column is full. Select another.",
                    level=MsgLevel.error
                )
            return await self.send_board(reaction.message.channel)

        if reaction.emoji == str(Emoji.five):
            try:
                session.play(user, 5)
            except ValueError:
                await self.send_message(
                    reaction.message.channel,
                    msg="That column is full. Select another.",
                    level=MsgLevel.error
                )
            return await self.send_board(reaction.message.channel)

        if reaction.emoji == str(Emoji.six):
            try:
                session.play(user, 6)
            except ValueError:
                await self.send_message(
                    reaction.message.channel,
                    msg="That column is full. Select another.",
                    level=MsgLevel.error
                )
            return await self.send_board(reaction.message.channel)

        if reaction.emoji == str(Emoji.seven):
            try:
                session.play(user, 7)
            except ValueError:
                await self.send_message(
                    reaction.message.channel,
                    msg="That column is full. Select another.",
                    level=MsgLevel.error
                )
            return await self.send_board(reaction.message.channel)

        if reaction.emoji == str(Emoji.x):
            session.forfeit()
            return await self.send_board(reaction.message.channel)

    @Cog.listener(name="on_timer_update")
    async def on_timer_update(self, sec: int):
        """Timer event that triggers every 1 second"""

        # Only check statuses every `self.timeout_incr` seconds
        if sec % self.timeout_incr == 0:

            # Get all sessions and start a list of ones that timed out
            sessions = self.sessions.values()
            to_expire = list()

            # Increment the time on all
            for session in sessions:
                session.timeout += self.timeout_incr

                # Timeout reached
                # Add to list of expired sessions
                if session.timeout == self.timeout:
                    to_expire.append(session)

            # Set game over condition on all expired sessions to timeout and send
            for session in to_expire:
                session.expire()
                await self.send_board(session.msg.channel)


def setup(bot: Bot):
    """ConnectFour"""
    bot.add_cog(ConnectFour(bot))
