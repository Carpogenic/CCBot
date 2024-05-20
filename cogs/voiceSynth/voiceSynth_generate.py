from openai import OpenAI
from config import OPENAI_API_KEY, ELEVENLABS_API_KEY
import aiohttp
import json

client = OpenAI()
OpenAI.api_key = OPENAI_API_KEY

async def generate_response(prompt):
    instruction = (
        "You are a helpful assistant designed to output JSON. Your response should be a JSON object with the following structure:\n"
        "{\n"
        '  "language": "Language",\n'
        '  "gender": "Gender of your synthesized voice (your choice)",\n'
        '  "response": "The content of the response"\n'
        "}\n"
        "For example:\n"
        '- If the prompt is in English, the response should be:\n'
        '  {\n'
        '    "language": "English",\n'
        '    "gender": "Male",\n'
        '    "response": "Your response here"\n'
        "  }\n"
        '- If the prompt is in Swedish, the response should be:\n'
        '  {\n'
        '    "language": "Swedish",\n'
        '    "gender": "Female",\n'
        '    "response": "Your response here"\n'
        "  }\n"
        "People will use your response to synthesize voice in a chat. We're all just messing around so get creative. The response should be 80 words or less."
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
        response_content = response.choices[0].message.content
        response_json = json.loads(response_content)
        return response_json
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process your request."


async def get_audio_stream(text, language, gender):
    # Define specific voice IDs for different languages and genders
    voices = {
        "English": {
            "Male": "EiNlNiXeDU1pqqOPrYMO",
            "Female": "E5rptoR2EGM14KAcXJV8"
        },
        "Swedish": {
            "Male": "EiNlNiXeDU1pqqOPrYMO",
            "Female": "piTKgcLEGmPE4e6mEKli"
        }
    }

    # Fallback voice ID if no match is found
    default_voice_id = "EiNlNiXeDU1pqqOPrYMO"

    # Select a voice ID based on language and gender
    voice_id = voices.get(language, {}).get(gender, default_voice_id)

    # Choose the appropriate model based on language
    model_id = "eleven_multilingual_v2"
    if language == "English":
        model_id = "eleven_monolingual_v1"

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(tts_url, headers=headers, json=data) as resp:
            if resp.status != 200:
                print(f"Elvenlabs API error: {resp.status}")
                print(await resp.text())
                return None
            return await resp.read()