from ast import alias
from typing import Optional
from discord.ext import commands
from datetime import datetime
from ..db import db
from discord import Embed

class PlaylistManager(commands.Cog, name="playlist_manager"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready_handler.cog_ready(self.qualified_name)
        print(f"[*] Cog ready: {self.qualified_name}")

    
    @commands.command(name="save_playlist", aliases=["sp", "savep"])
    @commands.guild_only()
    async def save_playlist(self, ctx, playlist_name:str, playlist_url: str):
        status, msg = db.save_playlist(ctx=ctx, name=playlist_name, url=playlist_url)
        if status: 
            embed = Embed(
                title=f'Your playlist was successfully saved!',
                description=f"Use `$playlist {playlist_name}` to see the customization options available.",
                colour=0x34C080,
                timestamp=datetime.utcnow(),
            )
        else:
            embed = Embed(
                title=f'Something went wrong!',
                description=f"{msg}",
                colour=0xBA0F30,
                timestamp=datetime.utcnow(),
            )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(PlaylistManager(bot))
    