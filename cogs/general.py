"""General Commands"""

import discord
from discord.ext import commands
from cogs.utils import checks


class General:
    """General use and utility commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='userinfo', no_private=True)
    async def userinfo(self, ctx, member: discord.Member = None):
        """Gets current server information for a given user

         [p]userinfo @user
         [p]userinfo username#discrim
         [p]userinfo userid"""

        if member is None:
            member = ctx.message.author

        roles = ", ".join(
            [r.name for r in sorted(
                member.roles,
                reverse=True
            ) if '@everyone' not in r.name]
        )
        if roles == '':
            roles = 'User has no assigned roles.'

        emb = {
            'embed': {
                'title': 'User Information For:',
                'description': '{0.name}#{0.discriminator}'.format(member),
                'color': getattr(discord.Colour, member.default_avatar.name)()
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
                    'value': member.created_at.strftime(
                        "%b. %d, %Y\n%I:%M %p"
                    ),
                    'inline': True
                },
                {
                    'name': 'Joined Server:',
                    'value': member.joined_at.strftime("%b. %d, %Y\n%I:%M %p"),
                    'inline': True
                },
            ]
        }

        embed = discord.Embed(**emb['embed'])  # TODO: EMBED FUNCTION/CLASS
        embed.set_author(**emb['author'])
        embed.set_thumbnail(url=member.avatar_url_as(format='png'))
        for field in emb['fields']:
            embed.add_field(**field)

        await ctx.channel.send(embed=embed)

    @checks.sudo()
    @commands.command(name='ping', hidden=True)
    async def ping(self, ctx):
        """Your basic `ping`"""
        await ctx.send('Pong')


def setup(bot):
    bot.add_cog(General(bot))
