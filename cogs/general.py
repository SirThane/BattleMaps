"""General Commands"""

# Site
from discord.colour import Colour
from discord.embeds import Embed
from discord.member import Member
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command

# Local
from utils.classes import Bot, Embed, SubRedis
from utils.checks import sudo


class General(Cog):
    """General use and utility commands."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = SubRedis(bot.db, "general")

        self.errorlog = bot.errorlog

    @command(name='userinfo', no_private=True)
    async def userinfo(self, ctx: Context, member: Member = None):
        """Gets current server information for a given user

         [p]userinfo @user
         [p]userinfo username#discrim
         [p]userinfo userid"""

        if member is None:
            member = ctx.message.author

        roles = ", ".join(
            [r.name for r in sorted(
                member.roles[1:-1],
                reverse=True
            ) if '@everyone' not in r.name]
        )
        if roles == '':
            roles = 'User has no assigned roles.'

        emb = {
            'embed': {
                'title': 'User Information For:',
                'description': '{0.name}#{0.discriminator}'.format(member),
                'colour': getattr(Colour, member.default_avatar.name)()
            },
            'author': {
                'name': '{0.name} || #{1.name}'.format(ctx.guild, ctx.channel),
                'icon_url': ctx.guild.icon_url
            },
            'fields': [
                {
                    'name': 'User ID',
                    'value': str(member.id),
                    'inline': True
                },
                {
                    'name': 'Display Name:',
                    'value': member.nick if not None
                    else '(no display name set)',
                    'inline': True
                },
                {
                    'name': 'Roles:',
                    'value': roles,
                    'inline': False
                },
                {
                    'name': 'Account Created:',
                    'value': member.created_at.strftime("%b. %d, %Y\n%I:%M %p"),
                    'inline': True
                },
                {
                    'name': 'Joined Server:',
                    'value': member.joined_at.strftime("%b. %d, %Y\n%I:%M %p"),
                    'inline': True
                },
            ]
        }

        embed = Embed(**emb['embed'])  # TODO: EMBED FUNCTION/CLASS
        embed.set_author(**emb['author'])
        embed.set_thumbnail(url=member.avatar_url_as(format='png'))
        for field in emb['fields']:
            embed.add_field(**field)

        await ctx.channel.send(embed=embed)

    @sudo()
    @command(name='ping', hidden=True)
    async def ping(self, ctx: Context):
        """Your basic `ping`"""
        await ctx.send('Pong')


def setup(bot: Bot):
    """General"""
    bot.add_cog(General(bot))
