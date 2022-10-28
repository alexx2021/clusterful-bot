from typing import Optional, Literal

import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context, Greedy


from utils.paginator import BaseButtonPaginator

class Paginator(BaseButtonPaginator):
        
    async def format_page(self, entries):
        newEntries = ""
        for thing in entries:
            newEntries = newEntries + f"{thing}\n"

        embed = discord.Embed(title=(f'Leaderboard'), color=0x7289da, description=f"{newEntries}")
        
        embed.set_footer(text='Page {0.current_page}/{0.total_pages}'.format(self))
        
        return embed



class Commands(commands.Cog, command_attrs=dict(hidden=False)):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.guild_only()
    @app_commands.command(description="See the server's leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        rankings = await self.bot.db.execute_fetchall('SELECT * FROM messagecount WHERE guild_id = ? ORDER BY message_count DESC', (interaction.guild_id,))
        if not rankings:
            return await interaction.followup.send("There are no people on the leaderboard!")
        
        desc = []
        for rank, row in enumerate(rankings, start=1):
            user_id = row[1]
            user_msg_count = row[2]

            playerStatus = await self.bot.db.execute("SELECT * FROM player_status WHERE guild_id = ? AND user_id = ?",(interaction.guild_id, user_id))
            playerStatus = await playerStatus.fetchone()
            if playerStatus:
                if playerStatus[2] == "OUT":
                    e = f"~~**{rank}**. <@{user_id}> | {user_msg_count} Messages~~"
                else:
                    e = f"**{rank}**. <@{user_id}> | {user_msg_count} Messages"
            else:
                e = f"**{rank}**. <@{user_id}> | {user_msg_count} Messages"

            desc.append(e)

        await Paginator.start(interaction.followup, entries=desc, per_page=10)
    
    @commands.hybrid_command(name="ping", description="hmmm")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send(f'Pong! 🏓 {round(self.bot.latency*1000)}ms')

    @commands.command(desc="Alexx only smh")
    @commands.is_owner()
    async def debug(self, ctx):
        rows = await self.bot.db.execute_fetchall('SELECT * FROM player_status')
        await ctx.send(rows)
        rows = await self.bot.db.execute_fetchall('SELECT * FROM guild_config')
        await ctx.send(rows)
        rows = await self.bot.db.execute_fetchall('SELECT * FROM messagecount')
        await ctx.send(rows)

    @commands.command(description="!sync -> global sync\n!sync ~ -> sync current guild\n!sync * -> copies all global app commands to current guild and syncs\n!sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)\n!sync id_1 id_2 -> syncs guilds with id 1 and 2")
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
            if not guilds:
                if spec == "~":
                    synced = await self.bot.tree.sync(guild=ctx.guild)
                elif spec == "*":
                    self.bot.tree.copy_global_to(guild=ctx.guild)
                    synced = await self.bot.tree.sync(guild=ctx.guild)
                elif spec == "^":
                    self.bot.tree.clear_commands(guild=ctx.guild)
                    await self.bot.tree.sync(guild=ctx.guild)
                    synced = []
                else:
                    synced = await self.bot.tree.sync()

                await ctx.reply(
                    f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
                )
                return

            ret = 0
            for guild in guilds:
                try:
                    await self.bot.tree.sync(guild=guild)
                except discord.HTTPException:
                    pass
                else:
                    ret += 1

            await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @app_commands.default_permissions()
    @app_commands.guild_only()
    @app_commands.command(description="Sets up the bot")
    async def setup(self, interaction: discord.Interaction, start_game_now: bool, game_player_role: discord.Role, lost_game_role: discord.Role, minimum_number_chars: int, minimum_number_words: int) -> None:
        if minimum_number_words <= 0:
            await interaction.response.send_message("minimum_number_words cannot be less than 0", ephemeral=True)
            return
        if minimum_number_chars <= 0:
            await interaction.response.send_message("minimum_number_chars cannot be less than 0", ephemeral=True)
            return
        await interaction.response.defer()

        existingConfig = await self.bot.db.execute('SELECT * FROM guild_config WHERE guild_id = ?',(interaction.guild_id,))
        existingConfig = await existingConfig.fetchone()
        if not existingConfig:
            await self.bot.db.execute('INSERT INTO guild_config VALUES (?, ?, ?, ?, ?, ?)',(interaction.guild_id, str(start_game_now), game_player_role.id, lost_game_role.id, minimum_number_chars, minimum_number_words))
            await self.bot.db.commit()
            await interaction.followup.send("Config set successfully!", ephemeral=True)
        else:
            await self.bot.db.execute('DELETE FROM guild_config WHERE guild_id = ?',(interaction.guild_id,))
            await self.bot.db.commit()
            await self.bot.db.execute('INSERT INTO guild_config VALUES (?, ?, ?, ?, ?, ?)',(interaction.guild_id, str(start_game_now), game_player_role.id, lost_game_role.id, minimum_number_chars, minimum_number_words))
            await self.bot.db.commit()
            await interaction.followup.send("Updated an existing config!", ephemeral=True)
              
    @app_commands.default_permissions()
    @app_commands.guild_only()
    @app_commands.command(description="Change someone's message count")
    async def edit_msg_count(self, interaction: discord.Interaction, member: discord.Member, new_msg_count: int):
        await interaction.response.defer()
        existingPlayer = await self.bot.db.execute('SELECT user_id FROM messagecount WHERE guild_id = ? AND user_id = ?',(interaction.guild_id, member.id))
        existingPlayer = await existingPlayer.fetchone()
        if not existingPlayer:
            await self.bot.db.execute('INSERT INTO messagecount VALUES (?, ?, ?)',(interaction.guild_id, member.id, new_msg_count))
            await self.bot.db.commit()
            await interaction.followup.send(f"{member}'s count has been updated to {new_msg_count}!")
        else:
            await self.bot.db.execute('UPDATE messagecount SET message_count = ? WHERE guild_id = ? AND user_id = ?', (new_msg_count, interaction.guild_id, member.id))
            await self.bot.db.commit()
            await interaction.followup.send(f"{member}'s count has been updated to {new_msg_count}!")

    @app_commands.default_permissions()
    @app_commands.guild_only()
    @app_commands.command(description="increase someone's message count by x amt")
    async def add_msg_count(self, interaction: discord.Interaction, member: discord.Member, amt_to_add: int):
        await interaction.response.defer()
        existingPlayer = await self.bot.db.execute('SELECT user_id, message_count FROM messagecount WHERE guild_id = ? AND user_id = ?',(interaction.guild_id, member.id))
        existingPlayer = await existingPlayer.fetchone()
        if not existingPlayer:
            await self.bot.db.execute('INSERT INTO messagecount VALUES (?, ?, ?)',(interaction.guild_id, member.id, amt_to_add))
            await self.bot.db.commit()
            await interaction.followup.send(f"{member}'s count has been updated to {amt_to_add}!")
        else:
            newValue = existingPlayer[1] + amt_to_add
            await self.bot.db.execute('UPDATE messagecount SET message_count = ? WHERE guild_id = ? AND user_id = ?', (newValue, interaction.guild_id, member.id))
            await self.bot.db.commit()
            await interaction.followup.send(f"{member}'s count has been updated to {newValue}!")

    @app_commands.default_permissions()
    @app_commands.guild_only()
    @app_commands.command(description="decrease someone's message count by x amt")
    async def subtract_msg_count(self, interaction: discord.Interaction, member: discord.Member, amt_to_subtract: int):
        await interaction.response.defer()
        existingPlayer = await self.bot.db.execute('SELECT user_id, message_count FROM messagecount WHERE guild_id = ? AND user_id = ?',(interaction.guild_id, member.id))
        existingPlayer = await existingPlayer.fetchone()
        if not existingPlayer:
            await self.bot.db.execute('INSERT INTO messagecount VALUES (?, ?, ?)',(interaction.guild_id, member.id, amt_to_subtract))
            await self.bot.db.commit()
            await interaction.followup.send(f"{member}'s count has been updated to {amt_to_subtract}!")
        else:
            newValue = existingPlayer[1] - amt_to_subtract
            await self.bot.db.execute('UPDATE messagecount SET message_count = ? WHERE guild_id = ? AND user_id = ?', (newValue, interaction.guild_id, member.id))
            await self.bot.db.commit()
            await interaction.followup.send(f"{member}'s count has been updated to {newValue}!")



async def setup(bot):
    await bot.add_cog(Commands(bot)) 