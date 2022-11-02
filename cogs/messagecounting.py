from wsgiref.simple_server import server_version
from discord.ext import commands
import discord

class MessageCounting(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 2, commands.BucketType.member
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
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
            serverConfig = await self.bot.db.execute('SELECT * FROM guild_config WHERE guild_id = ?',(message.guild.id,))
            serverConfig = await serverConfig.fetchone()
            if serverConfig: #if the guild has a config set
                if str(serverConfig[1]) == 'True': #ongoing game
                    if str(serverConfig[2]) in str(message.author.roles): #if user has player role
                        if not (str(serverConfig[3]) in str(message.author.roles)): #if loser role not in player roles
                            charRequirement = serverConfig[4]
                            wordRequirement = serverConfig[5]
                            if len(message.clean_content) >= charRequirement: #check char requirement
                                splitString = message.clean_content.split()
                                if len(splitString) >= wordRequirement: #check word req
                                    existingPlayer = await self.bot.db.execute('SELECT user_id, message_count FROM messagecount WHERE guild_id = ? AND user_id = ?',(message.guild.id, message.author.id))
                                    existingPlayer = await existingPlayer.fetchone()
                                    for wordThing in splitString:
                                        if len(wordThing) <= 2:
                                            splitString.remove(wordThing)
                                    pointsToAdd = len(splitString)
                                    if pointsToAdd > 10: #cap points per msg at 10
                                        pointsToAdd = 10
                                    #await message.channel.send(f"You earned {pointsToAdd}")
                                    if not existingPlayer:
                                        await self.bot.db.execute('INSERT INTO messagecount VALUES (?, ?, ?)',(message.guild.id, message.author.id, pointsToAdd))
                                        await self.bot.db.commit()
                                    else:
                                        await self.bot.db.execute('UPDATE messagecount SET message_count = ? WHERE guild_id = ? AND user_id = ?', (existingPlayer[1] + pointsToAdd, message.guild.id, message.author.id))
                                        await self.bot.db.commit()


        

async def setup(bot):
    await bot.add_cog(MessageCounting(bot)) 