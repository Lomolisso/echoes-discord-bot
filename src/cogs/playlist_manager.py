from ast import alias
from sqlite3 import Timestamp
from typing import Optional
from discord.ext import commands
from datetime import datetime
from discord import Embed
from ..echoes.echoes_cogs import EchoesCog 
from ..db import db

class PlaylistManager(EchoesCog, name="playlist_manager"):
    
    @commands.command(name="save_playlist", aliases=["sp", "savep"])
    async def save_playlist(self, ctx, playlist_name:str, playlist_url: str):
        status, msg = db.save_playlist(ctx=ctx, name=playlist_name, url=playlist_url)
        if status: 
            embed = Embed(
                title=f'Your playlist was successfully saved!',
                description=f"Use `$playlist {playlist_name}` to inspect it.",
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

    @commands.command(name="inspect_playlist", aliases=["insp", "playlist", "inspect"])
    async def inspect_playlist(self, ctx, playlist_name: str):
        playlist = db.get_playlist_by_name(playlist_name)
        embed = Embed(
            title = f"{playlist[0].capitalize()}\n",
            description = f"{playlist[4].capitalize()}.",
            colour = 0x34c080,
            timestamp=datetime.utcnow(),
        )

        embed.set_thumbnail(
            url=f"{playlist[7]}"
        )

        fields = [
            ("Privacy", f"`{playlist[6]}`", True),
            ("Times played", f"`{playlist[5]}`", True),
            ("Date of creation", f"`{playlist[8].strftime('%d/%m/%Y')}`", False),
            ("Playlist URL",f"To access the playlist **[click here]({playlist[1]})**.", False),
            ("Configuration", f"Use `conf {playlist[0]}`", False)
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text="Enjoy your playlist!")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(PlaylistManager(bot))
    