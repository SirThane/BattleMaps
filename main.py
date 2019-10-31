"""BattleMaps, a utility bot for working with Advance Wars
maps on the AWBW Discord server"""

import json

from asyncio import get_event_loop, sleep
from discord import Activity, Message
from discord.utils import get, oauth_url

from classes.bot import Bot
from cogs.utils.utils import StrictRedis


APP_NAME = "BattleMaps"  # BOT NAME HERE


LOOP = get_event_loop()

try:
    with open("redis.json", "r+") as redis_conf:
        conf = json.load(redis_conf)["db"]
except FileNotFoundError:
    raise FileNotFoundError("redis.json not found in running directory")


db = StrictRedis(**conf)
config = f"{APP_NAME}:config"

bot = Bot(db=db, app_name=APP_NAME, **db.hgetall(f"{config}:instance"))


@bot.listen()
async def timer_update(seconds):
    # Dummy listener
    return seconds


# TODO: Refactor into events cog or similar
async def init_timed_events(client: Bot):
    """Create a listener task with a tick-rate of 1s"""

    await bot.wait_until_ready()  # Wait for the bot to launch first
    client.secs = 0

    secs = 0  # Count number secs
    while True:
        client.dispatch("timer_update", secs)
        await timer_update(secs)
        secs += 1
        client.secs = secs
        await sleep(1)


@bot.event
async def on_ready():
    bot.app_info = await bot.application_info()

    bot.owner = get(bot.get_all_members(), id=bot.app_info.owner.id)

    await bot.change_presence(activity=Activity(name="around while setting up shop.", type=0))

    bot.loop.create_task(init_timed_events(bot))

    print(f"\n#-------------------------------#")

    for cog in db.lrange(f"{config}:initial_cogs", 0, -1):
        try:
            print(f"| Loading initial cog {cog}")
            bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            print(f"| Failed to load extension {cog}\n|   {type(e).__name__}: {e}")

    await bot.change_presence(activity=Activity(name=f"{bot.command_prefix}help for help", type=2))

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
async def on_message(message: Message):
    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(**db.hgetall(f"{config}:run"))
