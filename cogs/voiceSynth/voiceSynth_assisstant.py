from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI()
OpenAI.api_key = OPENAI_API_KEY

async def generate_voice_response(prompt):
    instruction = (
        "You are a helpful assistant designed to output JSON. Your response should be a JSON object with the following structure:\n"
        "{\n"
        '  "language": "Language",\n'
        '  "response": "The content of the response"\n'
        "}\n"
        "For example:\n"
        '- If the prompt is in English, the response should be:\n'
        '  {\n'
        '    "language": "English",\n'
        '    "response": "Your response here"\n'
        "  }\n"
        '- If the prompt is in Swedish, the response should be:\n'
        '  {\n'
        '    "language": "Swedish",\n'
        '    "response": "Your response here"\n'
        "  }\n"
        "People will use your response to synthesise voice in a chat. We're all just messing around so get creative. The response should be 80 words or less."
        "You never write dialogue from the point of view of the recipient."
    )
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process your request."
