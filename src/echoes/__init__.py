from discord import Intents
from datetime import datetime
from discord import Embed
from glob import glob
from .echoes_cogs import CogsReadyHandler
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..db import db

def get_cog_name(path: str) -> str:
    """ 
    Auxiliary function, gets a cog path and returns
    the name of the file without the '.py' 
    """
    return path.split("\\")[-1][:-3]


PREFIX = '$'
OWNER_IDS = [232211949788594186]
COGS = [get_cog_name(path) for path in glob("./src/cogs/*.py")]

class Echoes(Bot):

    def __init__(self):
        """ Echoes bot constructor """
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready_handler = CogsReadyHandler(COGS) 
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        
        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=PREFIX, 
            owners_id=OWNER_IDS,
            intents=Intents.all()   # Read docs about Intents.
        )
    
    def setup(self):
        """
        Loads the extensions such as cogs into the bot.
        """
        for cog_name in COGS:    
            self.load_extension(f"src.cogs.{cog_name}")

    def run(self, version):
        """ 
        Echoes run method, it is called when ./launcher.py
        is runned in the command line.
        """
        self.VERSION = version

        print("[*] Running echoes setup")
        self.setup()   # loads the extensions into the bot.

        with open("./src/echoes/token.txt", 'r', encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        
        print("[*] Echoes running...")

        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("[*] Echoes connected")
        
    async def on_disconnect(self):
        print("[*] Echoes disconnected")

    async def on_ready(self):
        if await self.cogs_ready_handler.ready():
            self.servers = 1
            self.guild = self.get_guild(398964348376055808)   # Only for single server bot.
            channel = self.get_channel(926180246116499566)    # echoes-debug txt channel id.
            self.scheduler.start()
            embed = Embed(
                title="Echoes is now online!",
                description="Use `$help` to view **「echoes」** commands.",
                colour=0x34c080,
                timestamp=datetime.utcnow(),
            )
            embed.set_author(
                name="Lomolisso",
                icon_url="https://avatars.githubusercontent.com/u/70459826?v=4",
                url="https://github.com/Lomolisso"
            )
            embed.set_thumbnail(
                url="https://i.imgur.com/kKz4srP.png"
            )
            fields = [
                ("Version", f"`{self.VERSION}`", False),
                ("Servers", f"Echoes is currently a member of `{self.servers}` server(s).", False)
            ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_footer(text="Share it with your friends!")

            await channel.send(embed=embed)
            print("[*] Echoes ready")
            self.ready = True

        else:
            print("[*] Echoes reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


echoes = Echoes()

@Bot.command(echoes)
async def reload_cog(ctx, cog_name: str):
    echoes.get_cog(cog_name).reload_cog()
    await ctx.send(f"```Cog {cog_name} reloaded!```")


