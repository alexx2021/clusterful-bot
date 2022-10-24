from typing import Optional, Literal

import discord
from discord.ext import commands
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


async def setup(bot):
    await bot.add_cog(Commands(bot)) 