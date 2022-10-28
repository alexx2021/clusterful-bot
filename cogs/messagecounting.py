from discord.ext import commands
import discord

class MessageCounting(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 10, commands.BucketType.member
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()

        if message.author == self.bot.user:
            return
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.channel.id in self.bot.ignored_channels:
            return

        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if not retry_after:
            print("counted")
            ongoingGame = await self.bot.db.execute('SELECT ongoing_game FROM guild_config WHERE guild_id = ?',(message.guild.id,))
            ongoingGame = await ongoingGame.fetchone()
            if str(ongoingGame[0]) == 'True':
                existingPlayer = await self.bot.db.execute('SELECT user_id, message_count FROM messagecount WHERE guild_id = ? AND user_id = ?',(message.guild.id, message.author.id))
                existingPlayer = await existingPlayer.fetchone()
                if not existingPlayer:
                    await self.bot.db.execute('INSERT INTO messagecount VALUES (?, ?, ?)',(message.guild.id, message.author.id, 1))
                    await self.bot.db.commit()
                else:
                    await self.bot.db.execute('UPDATE messagecount SET message_count = ? WHERE guild_id = ? AND user_id = ?', (existingPlayer[1] + 1, message.guild.id, message.author.id))
                    await self.bot.db.commit()

        




async def setup(bot):
    await bot.add_cog(MessageCounting(bot)) 