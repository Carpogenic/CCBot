import ollama
import copy

class ollamaHandler:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.chat_messages = {}
        self.system_message = "You are a helpful assistant who keeps their responses to 50 words or less."
        self.prepended_message = [{'role': 'user', 'content': 'please keep your responses fairly short, 150 words or less'}]

    async def create_message(self, message, role):
        return {
            'role': role,
            'content': message
        }

    async def generate_chat(self, guild_id):
        messages = self.chat_messages.setdefault(guild_id, copy.deepcopy(self.prepended_message))

        try:
            ollama_response = ollama.chat(model='llama3.2', stream=False, messages=messages)
            assistant_message = ollama_response['message']['content']

            messages.append(await self.create_message(assistant_message, 'assistant'))
            return assistant_message

        except Exception as e:
            print(f"Error in ollama_chat {e}")
            return f"Could not process request. Likely the server isn't on. \nError: {e}"

    async def user_message(self, ctx, prompt):
        guild_id = ctx.guild.id
        messages = self.chat_messages.setdefault(guild_id, copy.deepcopy(self.prepended_message))

        messages.append(await self.create_message(prompt, 'user'))

        assistant_reply = await self.generate_chat(guild_id)
        await ctx.send(assistant_reply)

    async def clear(self, ctx):
        guild_id = ctx.guild.id

        self.chat_messages[guild_id] = copy.deepcopy(self.prepended_message)
        await ctx.send("~~Chat~~ Talk history has been cleared.")