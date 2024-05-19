import discord

# drop down menu with the options you can vote for
class pollSelect(discord.ui.Select):
    def __init__(self, options, poll_view):
        super().__init__(placeholder='Choose an option...', min_values=1, max_values=1)
        self.poll_view = poll_view
        for index, option in enumerate(options, start=1):
            if option.strip():
                self.add_option(label=option, value=str(index))
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            user_id = interaction.user.id
            selected_index = int(self.values[0]) - 1
            selected_option = self.options[selected_index]

            # Check if the user has already voted
            if user_id in self.poll_view.user_votes:
                previous_index = self.poll_view.user_votes[user_id]
                
                # If the user is voting for the same option they previously voted for
                if previous_index == selected_index:
                    await interaction.followup.send("You have already voted for this option.", ephemeral=True)
                    return
                
                # If it's a different option, remove the previous vote
                self.poll_view.vote_counts[previous_index] -= 1

            # Record the new vote
            self.poll_view.vote_counts[selected_index] += 1
            self.poll_view.user_votes[user_id] = selected_index  # Update the user's vote

            await self.poll_view.update_embed(interaction)
            
            await interaction.followup.send(f"You voted for option: {selected_option}", ephemeral=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            await interaction.followup.send("An error occurred while processing your vote.", ephemeral=True)

# button to close the poll manually
class closePollButton(discord.ui.Button):
    def __init__(self, author: discord.User|discord.Member, label: str, poll_view: 'pollView'):
        super().__init__(style=discord.ButtonStyle.red, label=label)
        self.poll_view = poll_view
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # Ensure that only the poll creator can close the poll
        if interaction.user == self.author:
            await self.poll_view.close_poll()
        else:
            await interaction.response.send_message("You cannot kill what you did not create.", ephemeral=True)


# view that contains the drop down
class pollView(discord.ui.View):
    def __init__(self, author, options, timeout):
        super().__init__(timeout=timeout)
        self.options = options
        self.message = None
        self.vote_counts = [0] * len(options)
        self.user_votes = {}  # Dictionary to track each user's current vote
        self.add_item(closePollButton(author, label="Close Poll", poll_view=self))
        self.select = pollSelect(options, self)
        self.add_item(self.select)


    async def update_embed(self, interaction):
        embed = discord.Embed(title="Poll Results", description="Current votes:")
        for option, count in zip(self.options, self.vote_counts):
            embed.add_field(name=option, value=f"Votes: {count}", inline=False)
        await interaction.message.edit(embed=embed)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Here, you can add any checks you want, like ensuring only users who are part of the poll can vote.
        return True

    async def close_poll(self):
        highest_votes = max(self.vote_counts)

        # Find all options that have the highest number of votes
        winning_indices = [index for index, count in enumerate(self.vote_counts) if count == highest_votes]
        winning_options = [self.options[index] for index in winning_indices]
        
        # Prepare the result message
        if winning_options:
            winner_text = "\n".join(winning_options)
            result_text = "Voting has ended. The results are in."
        else:
            result_text = "Voting has ended. No votes were cast."

        embed = discord.Embed(title="Poll Results", description="Current votes:", color=discord.Color.brand_green())

        for option, count in zip(self.options, self.vote_counts):
            embed.add_field(name=option, value=f"Votes: {count}", inline=False)

        embed.add_field(name=f"---------------", value="               ", inline=False)
        embed.add_field(name=f"Winner{'' if len(winning_options) == 1 else 's'}", value=f"{winner_text}")

        self.clear_items()
        await self.message.edit(content=result_text, embed=embed, view=self)
        for item in self.children:
            item.disabled = True
        self.stop()


    async def on_timeout(self):
        await self.close_poll()

