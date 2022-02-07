from asyncio import sleep
from pickle import TRUE

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