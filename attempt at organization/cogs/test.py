from discord.ext import commands
import re

class testCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 177112397872365568 and re.search(r"^\.{3}$", message.content):
            await message.channel.send("ok this seems to be working")





async def setup(bot):
    await bot.add_cog(testCog(bot))


