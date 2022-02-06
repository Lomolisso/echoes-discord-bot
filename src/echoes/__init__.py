from discord import Intents
from datetime import datetime
from discord import Embed
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..db import db

PREFIX = '$'
OWNER_IDS = [232211949788594186]

class Echoes(Bot):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        
        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=PREFIX, 
            owners_id=OWNER_IDS,
            intents=Intents.all()   # Read docs about Intents.
        )
    
    def run(self, version):
        self.VERSION = version

        with open("./src/echoes/token.txt", 'r', encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        
        print("[*] Echoes running...")

        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("[*] Echoes connected")
        
    async def on_disconnect(self):
        print("[*] Echoes disconnected")

    async def on_ready(self):
        if not self.ready:
            self.ready = True
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
            embed.set_footer(text="Share it with your friends!")
            embed.set_author(
                name="Lomolisso",
                icon_url="https://avatars.githubusercontent.com/u/70459826?v=4",
                url="https://github.com/Lomolisso"
            )
            embed.set_thumbnail(
                url="https://64.media.tumblr.com/9348e0560a2d41919a71c5fe557c7a94/dc2a8493299949d9-fd/s540x810/e7b8c1f27674c207153149f9d7e03011a177a780.png"
            )
            fields = [
                ("Version", f"`{self.VERSION}`", False),
                ("Servers", f"Echoes is currently a member of `{self.servers}` server(s).", False)
            ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await channel.send(embed=embed)

        else:
            print("[*] Echoes reconnected")

    async def on_message(self, message):
        pass

echoes = Echoes()