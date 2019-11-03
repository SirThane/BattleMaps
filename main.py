# -*- coding: utf-8 -*-

"""BattleMaps, a utility bot for working with Advance Wars
maps on the AWBW Discord server"""

from json import load

from discord import Activity, Message
from discord.utils import get, oauth_url

from utils.classes import Bot
from utils.utils import StrictRedis


APP_NAME = "BattleMaps"  # BOT NAME HERE


"""
Minimum Redis Schema

:namespace {APP_NAME}:config:
    :HASH {APP_NAME}:config:instance
        :key command_prefix:    str         # Prefix for commands
        :key description:       str         # Description will be used for Help
        :key dm_help:           bool        # If Help output will be forced to DMs
    :HASH {APP_NAME}:config:run
        :key bot:               bool        # If bot account
        :key token              str         # Login token


Redis Configuration JSON Schema

:file ./redis.json
{
  "db": {
    "host": "localhost",                    # Server address hosting Redis DB
    "port": 6379,                           # Port for accessing Redis
    "db": 0,                                # Redis DB number storing app configs
    "decode_responses": true                # decode_responses must be bool true
  }
}
"""


try:
    with open("redis.json", "r+") as redis_conf:
        conf = load(redis_conf)["db"]
        db = StrictRedis(**conf)
except FileNotFoundError:
    raise FileNotFoundError("redis.json not found in running directory")


config = f"{APP_NAME}:config"

bot = Bot(db=db, app_name=APP_NAME, **db.hgetall(f"{config}:instance"))


@bot.event
async def on_ready():
    """Coroutine called bot is logged in and ready to receive commands"""

    # "Loading" status message
    loading = "around, setting up shop."
    await bot.change_presence(activity=Activity(name=loading, type=0))

    # Bot account metadata such as bot user ID and owner identity
    bot.app_info = await bot.application_info()
    bot.owner = get(bot.get_all_members(), id=bot.app_info.owner.id)

    print(f"\n#-------------------------------#")

    # Load all initial cog names stored in db
    for cog in db.lrange(f"{config}:initial_cogs", 0, -1):
        try:
            print(f"| Loading initial cog {cog}")
            bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            print(f"| Failed to load extension {cog}\n|   {type(e).__name__}: {e}")

    # "Ready" status message
    ready = f"{bot.command_prefix}help for help"
    await bot.change_presence(activity=Activity(name=ready, type=2))

    # Pretty printing ready message and general stats
    print(f"#-------------------------------#\n"
          f"| Successfully logged in.\n"
          f"#-------------------------------#\n"
          f"| Username:  {bot.user.name}\n"
          f"| User ID:   {bot.user.id}\n"
          f"| Owner:     {bot.owner}\n"
          f"| Guilds:    {len(bot.guilds)}\n"
          f"| Users:     {len(list(bot.get_all_members()))}\n"
          f"| OAuth URL: {oauth_url(bot.app_info.id)}\n"
          f"# ------------------------------#")


@bot.event
async def on_message(msg: Message):
    await bot.process_commands(msg)


if __name__ == "__main__":
    bot.run(**db.hgetall(f"{config}:run"))
