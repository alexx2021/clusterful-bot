from discord.ext import commands
import discord

class roleEvents(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        await self.bot.wait_until_ready()
        #print(f"role event fired in {after.guild.name}")
        outRole = await self.bot.db.execute('SELECT lost_game_player_role_id FROM guild_config WHERE guild_id = ?',(after.guild.id,))
        outRole = await outRole.fetchone()
        if outRole:
            outRole = str(outRole[0])
            
            if not (f"id={outRole}" in str(before.roles)):
                #print("outrole not in before list")
                if f"id={outRole}" in str(after.roles):
                    #print("outrole in after list")
                    existingPlayer = await self.bot.db.execute('SELECT user_id FROM player_status WHERE guild_id = ? AND user_id = ?',(after.guild.id, after.id))
                    existingPlayer = await existingPlayer.fetchone()
                    if not existingPlayer:
                        await self.bot.db.execute('INSERT INTO player_status VALUES (?, ?, ?)',(after.guild.id, after.id, "OUT") )
                        await self.bot.db.commit()
                    else:
                        await self.bot.db.execute('UPDATE player_status SET status = ? WHERE guild_id = ? AND user_id = ?', ("OUT", after.guild.id, after.id))
                        await self.bot.db.commit()
            else:
                #print("outrole in before list")
                if not (f"id={outRole}" in str(after.roles)):
                    #print("outrole not in after list")
                    await self.bot.db.execute('DELETE FROM player_status WHERE guild_id = ? AND user_id = ?', (after.guild.id, after.id))
                    await self.bot.db.commit()






        # print("============================")
        # print(before.name)
        # print(before.roles)
        # print("----------------------------")
        # print(after.name)
        # print(after.roles)
        # print("============================")




async def setup(bot):
    await bot.add_cog(roleEvents(bot)) 