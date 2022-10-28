from ast import Interactive
from typing import Optional, Literal

import discord
from discord.ext import commands
from discord import app_commands
from discord import Object
from discord.ext.commands import Context, Greedy


from utils.paginator import BaseButtonPaginator

class Paginator(BaseButtonPaginator):
        
    async def format_page(self, entries):
        embed = discord.Embed(title=(f'Queue'), color=0x7289da)
        for index, entry in enumerate(entries):
            embed.add_field(name=str(index), value=entry)
        
        embed.set_footer(text='Page {0.current_page}/{0.total_pages}'.format(self))
        
        return embed



class Commands(commands.Cog, command_attrs=dict(hidden=False)):
    def __init__(self, bot):
        self.bot = bot
    
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
    async def setup(self, interaction: discord.Interaction, start_game_now: bool, game_player_role: discord.Role, lost_game_role: discord.Role, minimum_number_chars: int, minimum_number_spaces: int) -> None:
        if minimum_number_spaces <= 0:
            await interaction.response.send_message("minimum_number_spaces cannot be less than 0", ephemeral=True)
            return
        if minimum_number_chars <= 0:
            await interaction.response.send_message("minimum_number_chars cannot be less than 0", ephemeral=True)
            return
        await interaction.response.defer()

        existingConfig = await self.bot.db.execute('SELECT * FROM guild_config WHERE guild_id = ?',(interaction.guild_id,))
        existingConfig = await existingConfig.fetchone()
        if not existingConfig:
            #guild_id INTERGER, ongoing_game TEXT, game_player_role_id INTERGER, lost_game_player_role_id INTERGER, num_chars INTERGER, num_spaces INTERGER
            await self.bot.db.execute('INSERT INTO guild_config VALUES (?, ?, ?, ?, ?, ?)',(interaction.guild_id, str(start_game_now), game_player_role.id, lost_game_role.id, minimum_number_chars, minimum_number_spaces))
            await self.bot.db.commit()
            await interaction.followup.send("Config set successfully!", ephemeral=True)
        else:
            await self.bot.db.execute('DELETE FROM guild_config WHERE guild_id = ?',(interaction.guild_id,))
            await self.bot.db.commit()
            await self.bot.db.execute('INSERT INTO guild_config VALUES (?, ?, ?, ?, ?, ?)',(interaction.guild_id, str(start_game_now), game_player_role.id, lost_game_role.id, minimum_number_chars, minimum_number_spaces))
            await self.bot.db.commit()
            await interaction.followup.send("Updated an existing config!", ephemeral=True)
        


async def setup(bot):
    await bot.add_cog(Commands(bot)) 