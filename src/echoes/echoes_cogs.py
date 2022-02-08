from asyncio import sleep
from discord.ext import commands

class EchoesCog(commands.Cog):
    """
    Parent class of all the cogs of the Echoes bot.
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready_handler.cog_ready(self.qualified_name)
        print(f"[*] Cog ready: {self.qualified_name}")

    def reload_cog(self):
        self.bot.reload_extension(f"src.cogs.{self.qualified_name}")
        print(f"[*] Cog reloaded: {self.qualified_name}")


class CogsReadyHandler:
    """
    Auxiliary class, allows the bot to load all the cogs
    before executing the code in the on_ready corroutine.
    """
    def __init__(self, cogs: list):
        self.__cogs_remaining = len(cogs)
        self.__cogs_status = {}
        for cog_name in cogs:
            self.__cogs_status[cog_name] = False

    def cog_ready(self, cog_name: str) -> None:
        if not self.__cogs_status[cog_name]:
            self.__cogs_status[cog_name] = True
            self.__cogs_remaining -= 1
    
    async def ready(self):
        while self.__cogs_remaining != 0:
            await sleep(0.1)
        return True