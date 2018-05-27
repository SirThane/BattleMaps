"""BattleMaps, a utility bot for working with Advance Wars
maps on the AWBW Discord server"""

import asyncio
import json

import discord
from discord.ext import commands

from cogs.utils import utils


LOOP = asyncio.get_event_loop()

APP_NAME = 'BattleMaps'  # BOT NAME HERE

try:
    with open('redis.json', 'r+') as redis_conf:
        conf = json.load(redis_conf)["db"]
except FileNotFoundError:
    conf = None  # STHU, PyCharm
    print('ERROR: redis.json not found in running directory')
    exit()


db = utils.StrictRedis(**conf)
config = f'{APP_NAME}:config'
bot = commands.Bot(
    command_prefix=db.hget(f'{config}:prefix', 'default'),
    **db.hgetall(f'{config}:instance')  # TODO: Refactor
)
bot.db = db
bot.APP_NAME = APP_NAME


@bot.listen()
async def timer_update(seconds):
    # Dummy listener
    return seconds


# TODO: Refactor into events cog or similar
async def init_timed_events(client: commands.Bot):
    """Create a listener task with a tick-rate of 1s"""

    await bot.wait_until_ready()  # Wait for the bot to launch first
    client.secs = 0

    secs = 0  # Count number secs
    while True:
        client.dispatch("timer_update", secs)
        await timer_update(secs)
        secs += 1
        client.secs = secs
        await asyncio.sleep(1)


@bot.event
async def on_ready():
    bot.app_info = await bot.application_info()

    bot.owner = discord.utils.get(
        bot.get_all_members(),
        id=bot.app_info.owner.id
    )

    await bot.change_presence(game=discord.Game(name="setting up shop."))

    bot.loop.create_task(init_timed_events(bot))

    print(f'\n'
          f'#-------------------------------#')

    for cog in db.lrange(f'{config}:initial_cogs', 0, -1):
        try:
            print(f'| Loading initial cog {cog}')
            bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            print(
                '| Failed to load extension {}\n|   {}: {}'.format(
                    cog,
                    type(e).__name__,
                    e
                )
            )

    print(f'#-------------------------------#\n')

    await bot.change_presence(
        game=discord.Game(
            name=f'{bot.command_prefix}help'
        )
    )

    print(f'#-------------------------------#\n'
          f'| Successfully logged in.\n'
          f'#-------------------------------#\n'
          f'| Username:  {bot.user.name}\n'
          f'| User ID:   {bot.user.id}\n'
          f'| Owner:     {bot.owner}\n'
          f'| Guilds:    {len(bot.guilds)}\n'
          f'| Users:     {len(list(bot.get_all_members()))}\n'
          f'| OAuth URL: {discord.utils.oauth_url(bot.app_info.id)}\n'
          f'# ------------------------------#')


@bot.event
async def on_message(message):
    await bot.process_commands(message)


if __name__ == "__main__":
    run = {
        'token': db.hget(f'{config}:run', 'token'),
        'bot': db.hget(f'{config}:run', 'bot')
    }
    bot.run(run['token'], bot=run['bot'])
