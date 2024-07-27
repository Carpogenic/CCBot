import discord
from discord.ext import commands
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI()
OpenAI.api_key = OPENAI_API_KEY

class kyuuBackupCog(commands.Cog):

    @commands.command()
    async def bask(self, ctx, *, prompt): # backup ask
        instruction = (
            "You are a helpful assistant. Your response should be 80 words or less, unless necessary for a full answer."
        )
        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt}
        ]
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            
            await ctx.send(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "Sorry, I couldn't process your request."

async def setup(bot):
    await bot.add_cog(kyuuBackupCog(bot))