import os
import openai
from dotenv import find_dotenv, load_dotenv
from langchain_community.llms import OpenAI
import json

VOICES_FILE = "available_voices.txt"



with open(VOICES_FILE, "r", encoding="utf-8") as f:
    voices = [line.strip() for line in f if line.strip()]


load_dotenv(find_dotenv())

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

response = client.responses.create(
    model="openai/gpt-oss-20b",
    input=input("Enter your prompt: "),
)

response=response.output_text

classifyHuman = f"""
You are given:
1) A paragraph of text in any language. From this, you must identify the most likely persona (e.g., man, woman, child, elderly person, animated character, narrator, etc.).
2) A whitelist of valid Microsoft Edge TTS ShortNames. This list is case-sensitive, and you MUST select the exact casing from it.
Available voices:
{voices}

Your task:
1. Identify the persona implied by the paragraph in a short descriptive phrase.
   - Example: "elderly Indian male storyteller", "young Japanese female narrator", "child speaking Spanish with excitement".
   - Consider cultural background, gender, age, and emotional tone implied in the text.
   - Support all languages; if the paragraph is in a language other than English, choose a voice in that language from the available list.
   - If no perfect match exists in the same language, choose the closest cultural and linguistic match.
   - Do not give empty strings or null values.
2. Select a Microsoft Edge TTS voice ShortName from the available voices list that best matches the persona.
   - Must be EXACTLY as it appears in the list, preserving exact case.
   - Do not give empty strings or null values.
3. Suggest a narration rate (Edge TTS 'rate' parameter) based on the persona's speaking style.
   - Output as a signed integer string without the % symbol (e.g., "+5", "-10", "+0").
   - Positive = slightly faster, negative = slightly slower, +0 = default.
   - Match the expected pace for that language and persona while keeping it natural.
   - Do not give empty strings or null values.
4. Suggest a pitch (Edge TTS 'pitch' parameter) based on the persona's speaking style.
   - Output as a signed integer string without the Hz suffix (e.g., "+20", "-20", "+0").
   - Positive = higher pitch, negative = lower pitch, +0 = default.
   - Choose a natural value for the language and persona.
   - Do not give empty strings or null values.
5. Suggest a tone for the persona in a single descriptive word (e.g., "cheerful", "authoritative", "calm", "dramatic", "empathetic").
   - Always output in lowercase English.
   - Output as a single string.
   - Do not give empty strings or null values.

Output:
- Provide ONLY a valid JSON object with keys: "persona", "voice", "rate", "pitch", "tone".
- All values must be strings.
- No arrays, no nested objects, no additional keys, no explanations.

Paragraph: {response}
 """

resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": classifyHuman}],
    )
character=resp.choices[0].message.content.strip().lower()

print(character)

character = json.loads(character)


for k, v in character.items():
    if not isinstance(v, str):
        character[k] = str(v)
matches = [v for v in voices if v.lower() == character['voice'].lower()]

character['voice'] = matches[0]
if not character['voice']:
    character['voice'] = "en-US-JennyNeural"
    
print(character)

