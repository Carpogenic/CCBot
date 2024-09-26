import ollama

class ollamaHandler:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.chat_messages = [{'role': 'user', 'content': 'please keep your responses fairly short, 150 words or less'}]
        self.system_message = "You are a helpful assistant who keeps their responses to 50 words or less."

    async def create_message(self, message, role):
        return {
            'role': role,
            'content': message
        }
    
    async def chat(self):
        ollama_response = ollama.chat(model='llama3.1', stream=False, messages=self.chat_messages)
        assistant_message = ollama_response['message']['content']

        self.chat_messages.append(await self.create_message(assistant_message, 'assistant'))
        return assistant_message

    async def ask(self, ctx, prompt):
        self.chat_messages.append(await self.create_message(prompt, 'user'))
        await ctx.send(await self.chat())

    async def clear(self):
        self.chat_messages = [{'role': 'user', 'content': 'please keep your responses fairly short, 150 words or less'}]