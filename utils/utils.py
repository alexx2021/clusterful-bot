import discord
####################################################################################
async def setup(bot):
    await bot.mark.execute("CREATE TABLE IF NOT EXISTS messagecount(user_id INTERGER, messagecount INTERGER)")
    await bot.mark.execute("CREATE TABLE IF NOT EXISTS messagecount(guild_id INTERGER, role_id INTERGER, ongoing_game INTERGER)")
####################################################################################
async def get_or_fetch_channel(self, channel_id):
    """Only queries API if the channel is not in cache."""
    await self.bot.wait_until_ready()
    ch = self.bot.get_channel(int(channel_id))
    if ch:
        return ch

    try:
        ch = await self.bot.fetch_channel(int(channel_id))
    except discord.HTTPException:
        return None
    else:
        return ch

async def gech_main(bot, channel_id):
    """Gech func for instances where there is no "self" available"""
    await bot.wait_until_ready()
    ch = bot.get_channel(int(channel_id))
    if ch:
        return ch

    try:
        ch = await bot.fetch_channel(int(channel_id))
    except discord.HTTPException:
        return None
    else:
        return ch

async def get_or_fetch_member(self, guild, member_id):
    """Only queries API if the member is not in cache."""
    member = guild.get_member(int(member_id))
    if member is not None:
        return member

    try:
        member = await guild.fetch_member(int(member_id))
    except discord.HTTPException:
        return None
    else:
        return member

async def get_or_fetch_guild(self, guild_id):
    """Only queries API if the guild is not in cache."""
    guild = self.bot.get_guild(int(guild_id))
    if guild is not None:
        return guild

    try:
        guild = await self.bot.fetch_guild(int(guild_id))
    except discord.HTTPException:
        return None
    else:
        return guild
####################################################################################