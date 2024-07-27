import discord
from .poll_view import pollView


class pollModal(discord.ui.Modal):
    def __init__(self, author, options):
           super().__init__(title="Enter Poll Options")
           self.required=True
           self.author = author
           for i in range(options):
            self.add_item(discord.ui.TextInput(label=f"Option {i+1}", required=True if i<=1 else False, style=discord.TextStyle.short))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        options = [self.children[i].value for i in range(len(self.children)) if self.children[i].value.strip()]
        
        view = pollView(self.author, options, timeout=899) # longest timeout before the webhook token expires
        embed = discord.Embed(title="Poll Results", description="Current votes:")
        for option in options:
            embed.add_field(name=option, value="Votes: 0", inline=False)

        await interaction.response.send_message("Vote for an option:", view=view, ephemeral=False, embed=embed)
        view.message = await interaction.original_response()
        
        

        

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        print(f"Error with pollModal{Exception}")
        await interaction.response.send_message("something went wrong", ephemeral=True)

 