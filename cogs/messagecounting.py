from discord.ext import commands
import discord

class MessageCounting(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()

        if message.author == self.bot.user:
            return
        if message.author.bot:
            return
        if not message.guild:
            return




async def setup(bot):
    await bot.add_cog(MessageCounting(bot)) 