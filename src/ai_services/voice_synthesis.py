import asyncio
import edge_tts
import os

DIRECTORY = os.path.join('src','media','audio')
OUTPUT = "textToSpeech.mp3"

async def listEnglishVoices():
    voices = await edge_tts.list_voices()
    for voice in voices:
        if voice["Locale"].startswith("en"):
            print(f"{voice['ShortName']}")


async def synthesize(text,voice):
    tts = edge_tts.Communicate(text=text,voice=voice)
    await tts.save(os.path.join(DIRECTORY,OUTPUT))

def getVoice():
    voice = input("Enter the voice name: ")
    return voice

def getText():
    text = input("Enter the text to synthesize: ")
    return text

async def selectEnglishVoice():
    await listEnglishVoices()
    voice = getVoice()
    return voice
    

async def main():
    voice = await selectEnglishVoice()
    text = getText()
    await synthesize(text,voice)


if __name__ == "__main__":
    asyncio.run(main())
