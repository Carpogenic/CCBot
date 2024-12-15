from ollama import AsyncClient
import copy

class ollamaHandler:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.chat_messages = {}
        self.system_message = "You are a helpful assistant who keeps their responses to 50 words or less."
        self.prepended_message = [{'role': 'user', 'content': 'please keep your responses fairly short, 150 words or less', 'images': None}]
        self.model = 'llama3.2'

    async def create_message(self, message, role, image=None):
        return {
            'role': role,
            'content': message,
            'images': [image] if image else None
        }

    async def generate_chat(self, ctx, guild_id):
        messages = self.chat_messages.setdefault(guild_id, copy.deepcopy(self.prepended_message))

        client = AsyncClient()
        try:
            ollama_response = await client.chat(model=self.model, stream=False, messages=messages)
            assistant_message = ollama_response['message']['content']

            messages.append(await self.create_message(assistant_message, 'assistant'))
            print(self.model)
            return assistant_message

        except Exception as e:
            print(f"Error in ollama_chat {e}")
            return f"Could not process request.\nError: {e}"

    async def user_message(self, ctx, prompt):
        guild_id = ctx.guild.id
        image = None

        if len(ctx.message.attachments) > 0:
            attachment = ctx.message.attachments[0]
            if await self.is_image(attachment):
                image = await attachment.read()
            else:
                await ctx.send("The attached file is not a supported image type.")
                return


        use_vision = image is not None or await self.has_image_in_history(guild_id)
        self.model = 'llama3.2' if use_vision else 'llama3.2' # goodbye gpu ;_;7

        messages = self.chat_messages.setdefault(guild_id, copy.deepcopy(self.prepended_message))

        messages.append(await self.create_message(prompt, 'user', image))

        assistant_reply = await self.generate_chat(ctx, guild_id)
        await ctx.send(assistant_reply)


    async def has_image_in_history(self, guild_id):
        messages = self.chat_messages.get(guild_id, [])
        for message in messages:
            if message.get("images"):
                return True
        return False

    async def is_image(self, attachment):
        if attachment.content_type and attachment.content_type.startswith("image/"):
            print("mime type")
            return True

        print("extension")
        image_extensions = (".jpg", ".jpeg", ".png", ".webp")
        return attachment.filename.lower().endswith(image_extensions)

    async def clear(self, ctx):
        guild_id = ctx.guild.id
        self.model = 'llama3.2'

        self.chat_messages[guild_id] = copy.deepcopy(self.prepended_message)
        await ctx.send("~~Chat~~ Talk history has been cleared.")
