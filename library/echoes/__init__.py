from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

PREFIX = '$'
OWNER_IDS = "232211949788594186"

class Echoes(Bot):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler

        super().__init__(command_prefix=PREFIX, owners_id=OWNER_IDS)
    
    def run(self, version):
        self.VERSION = version

        with open("./library/echoes/token", 'r', encoding="utf-8") as tf:
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
            self.guild = self.get_guild("398964348376055808")   # Only for single server bot.
            print("[*] Echoes ready")
        
        else:
            print("[*] Echoes reconnected")

    async def on_message(self, message):
        pass

echoes = Echoes()