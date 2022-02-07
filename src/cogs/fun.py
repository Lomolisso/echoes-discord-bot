from discord.ext import commands

class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready_handler.cog_ready(self.qualified_name)
        print(f"[*] Cog ready: {self.qualified_name}")


def setup(bot):
    bot.add_cog(Fun(bot))