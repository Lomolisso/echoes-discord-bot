from discord import Embed, Interaction, ButtonStyle
from discord.ui import button, View
from discord.ext import commands
from datetime import datetime
from typing import Optional
from ..echoes.echoes_cogs import EchoesCog 
from ..db.db import Playlist

class PaginatorView(View):
    def __init__(self, pages: list[Embed], *, timeout: Optional[float] = 180):
        self.page_index = 0
        self.pages = pages
        super().__init__(timeout=timeout)
    
    @button(label="⪻", custom_id="first_button", style=ButtonStyle.primary)
    async def first_button_callback(self, button, interaction: Interaction):
        self.page_index = 0
        await interaction.response.edit_message(embed=self.pages[self.page_index], view=self)

    @button(label="🡰", custom_id="prev_button", style=ButtonStyle.primary)
    async def prev_button_callback(self, button, interaction: Interaction):
        if self.page_index > 0:
            self.page_index -= 1
            await interaction.response.edit_message(embed=self.pages[self.page_index], view=self)

    @button(label="♬", custom_id="play_button", style=ButtonStyle.green)
    async def play_button_callback(self, button, interaction: Interaction):
        pass

    @button(label="🡲", custom_id="next_button", style=ButtonStyle.primary)
    async def next_button_callback(self, button, interaction: Interaction):
        if self.page_index < len(self.pages) - 1:
            self.page_index += 1
            await interaction.response.edit_message(embed=self.pages[self.page_index], view=self)

    @button(label="⪼", custom_id="last_button", style=ButtonStyle.primary)
    async def last_button_callback(self, button, interaction: Interaction):
        self.page_index = len(self.pages) - 1
        await interaction.response.edit_message(embed=self.pages[self.page_index], view=self)

class PlaylistManager(EchoesCog, name="playlist_manager"):
    """
    This class is in charge of all the playlist related interactions,
    from saving a new one to the database to generating statistics
    and rankings using the data stored.
    """

    @commands.group(name="playlist", invoke_without_command=True)
    async def playlist(self, ctx):
        await ctx.send("```Playlist base command.```")

    @playlist.command(name="create")
    async def create_playlist(self, ctx, playlist_name:str, playlist_url: str):
        """
        This command allows a user to create a new playlist and save it to the db.

        Syntax: 
            >>> $playlist create <playlist_name> <playlist_url>

        """
        status, msg = Playlist.create(
            name=playlist_name, 
            url=playlist_url,
            owner_name=ctx.author.display_name,
            owner_id=ctx.author.id
        )

        embed = self.__generate_create_playlist_embed(playlist_name) if status else self.__generate_error_embed(msg)
        await ctx.send(embed=embed)

    @playlist.command(name="inspect")
    async def inspect_playlist(self, ctx, playlist_name: str) -> None:
        """
        This command allows a user to inspect a existing playlist.

        Syntax: 
            >>> $playlist inspect <playlist_name> <playlist_url>
        
        """
        playlist = Playlist.get_by_name(playlist_name)

        if playlist is None:
            embed = self.__generate_error_embed(f"The playlist {playlist_name} does not exist.")
        else:
            embed = self.__generate_inspect_embed(playlist, playlist['name'].capitalize())

        await ctx.send(embed=embed)

    @playlist.command(name="configure", aliases=["conf"])
    async def configure_playlist(self, ctx, playlist_name: str = None, property_name: str = None, value: str = None):
        """
        This command allows a user to configure a existing playlist.

        Syntax: 
            >>> $playlist configure <playlist_name> <property_name> <value>
        
        """
        if (playlist_name or property_name or value) is None:
            msg = """The correct syntax for this command is:
            ```$playlist configure <name> <property> <value>```"""
            embed = self.__add_modifiable_fields_to_embed(self.__generate_error_embed(msg=msg))
        else:
            playlist = Playlist.get_by_name(playlist_name)
            if playlist is None:
                embed = self.__generate_error_embed(msg=f"The playlist `{playlist_name}` does not exists.")
            elif ctx.author.id != playlist["owner_id"]:
                embed = self.__generate_error_embed(msg="You are not allowed to modify this playlist.")
            else:
                embed = self.__configure_playlist(playlist_name, property_name, value)
        await ctx.send(embed=embed)
    

    @playlist.command(name="ranking", aliases=["rank", "rankings"])
    async def ranking_playlist(self, ctx):
        """
        This command displays a ranking with the most popular playlists.

        Syntax: 
            >>> $playlist ranking
        
        """
        ranking = Playlist.get_ranking()
        pages = []
        for k, playlist in zip(range(1, len(ranking)+1), ranking):
            pages.append(self.__generate_inspect_embed(playlist, f"Top {k}: {playlist['name'].capitalize()}"))
        
        await ctx.send(embed=pages[0], view=PaginatorView(pages))

        
    def __generate_create_playlist_embed(self, playlist_name: str) -> Embed:
        embed = Embed(
                title=f'Your playlist was successfully saved!',
                description=f"Use `$playlist inspect {playlist_name}` to view it.",
                colour=0x34C080,
                timestamp=datetime.utcnow(),
        )
        return embed
    
    def __generate_error_embed(self, msg: str) -> Embed:
        embed = Embed(
            title=f'Something went wrong!',
            description=f"{msg}",
            colour=0xBA0F30,
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(
            url="https://i.imgur.com/9PUoaUv.png"
        )
        embed.set_footer(text="Oops!")
        return embed
    
    def __generate_inspect_embed(self, playlist: dict, title: str) -> Embed:
        embed = Embed(
                title = f"{title}\n",
                description = f"{playlist['description'].capitalize()}.",
                colour = 0x34c080,
                timestamp=datetime.utcnow(),
            )
        embed.set_thumbnail(
            url=f"{playlist['icon_url']}"
        )
        fields = [
            ("Privacy", f"`{playlist['privacy']}`", True),
            ("Times played", f"`{playlist['times_played']}`", True),
            ("Date of creation", f"`{playlist['created_at'].strftime('%d/%m/%Y')}`", False),
            ("Playlist URL",f"To access the playlist **[click here]({playlist['url']})**.", False),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_footer(text="Enjoy your playlist!")
        return embed
    
    def __add_editable_fields_to_embed(self, embed: Embed) -> Embed:
        properties = "```"
        properties += "-> name:                     [max 100 chars]\n"
        properties += "-> url:                                [url]\n"
        properties += "-> description:              [max 255 chars]\n"
        properties += "-> privacy:                 [public/private]\n"
        properties += "-> icon_url:                           [url]"
        properties += "```"
        
        embed.add_field(name="The available properties are the following:", value=properties, inline=False)
        return embed
    
    def __configure_playlist(self, playlist_name: str, property_name: str, value: str) -> Embed:
        status, msg = Playlist.set_property(playlist_name, property_name, value)
        if not status:
            embed = self.__add_editable_fields_to_embed(self.__generate_error_embed(msg=msg))
        else:
            _playlist_name = playlist_name if property_name != 'name' else value
            embed = Embed(
                title=f'Your playlist was successfully modified!',
                description=f"Use `$playlist inspect {_playlist_name}` to view it.",
                colour=0x34C080,
                timestamp=datetime.utcnow(),
            )
        return embed
         
def setup(bot):
    bot.add_cog(PlaylistManager(bot))    