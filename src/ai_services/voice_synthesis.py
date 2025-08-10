import asyncio
import edge_tts
import os

DIRECTORY = os.path.join('src','media','audio')
OUTPUT = "textToSpeech.mp3"
async def listEnglishVoices():
    try: 
        voices = await edge_tts.list_voices()
        for voice in voices:
            if voice["Locale"].startswith("te-IN"):
                print(f"{voice['ShortName']}")
    except Exception as e:
        print(f"Error listing voices: {e}")

async def synthesize(text,voice):
    try:
        tts = edge_tts.Communicate(text=text,voice=voice)
        await tts.save(os.path.join(DIRECTORY,OUTPUT))
    except Exception as e:
        print(f"Error synthesizing text: {e}")

async def validateVoice(voice):
    try:
        voices = await edge_tts.list_voices()
        for v in voices:
            if v["ShortName"] == voice:
                return True
        return False
    except Exception as e:
        print(f"Error validating voice: {e}")
        return False

async def getVoice():
    try:
        voice = input("Enter the voice name: ")
        if not await validateVoice(voice):
            print("Invalid voice name. Please try from above list of voices again.")
            return await getVoice()
        return voice
    except Exception as e:
        print(f"Error getting voice: {e}")
        return None

def getText():
    try:
        text = input("Enter the text to synthesize: ")
        return text
    except Exception as e:
        print(f"Error getting text: {e}")
        return None

async def selectEnglishVoice():
    try:
        await listEnglishVoices()
        voice = await getVoice()
        return voice
    except Exception as e:
        print(f"Error selecting voice: {e}")
        return None
    

async def main():
    try:
        voice = await selectEnglishVoice()
        text = getText()
        await synthesize(text,voice)
    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    asyncio.run(main())