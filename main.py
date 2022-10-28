import asyncio
import discord
from discord.ext import commands
import logging
import logging.handlers
from dotenv import load_dotenv
import os
import aiosqlite
from utils.utils import setup

load_dotenv()


logger = logging.getLogger('discord')
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.invites = False

bot = commands.Bot(command_prefix=(f'<@!{1033899131275579623}> ', f'<@{1033899131275579623}> ', "!"),
case_insensitive=True, 
intents=intents, 
allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False), 
activity=discord.Streaming(name=f"!help", url='https://www.twitch.tv/alexxwastakenlol')
)


#counts number of loaded extensions
bot.extension_count = 0

#global database connections
loop = asyncio.get_event_loop()
bot.db = loop.run_until_complete(aiosqlite.connect('bot.db'))

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print('--------------------------')
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    print(f'{bot.extension_count} total extensions loaded')
    print(f"Servers - {str(len(bot.guilds))}")
    print('--------------------------')
    print('Bot is ready!')       

extensions = (
    "commands",
    "messageCounting",
    "roleEvents",
    "errors",

    )

async def main():
    # start the bot
    async with bot:
        await setup(bot)

        for ext in extensions:
            await bot.load_extension(f"cogs.{ext}")
            print(f'Loaded {ext}')
            bot.extension_count += 1

        await bot.load_extension("jishaku")

        TOKEN = os.getenv("DISCORD_TOKEN")
        await bot.start(TOKEN)
 

asyncio.run(main())


