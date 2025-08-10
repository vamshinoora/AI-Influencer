import asyncio
import edge_tts
import os

DIRECTORY = os.path.join('src','media','audio')
OUTPUT = "textToSpeech.mp3"
async def listEnglishVoices():
    try: 
        voices = await edge_tts.list_voices()
        for voice in voices:
            if voice["Locale"].startswith("en-US"):
                print(f"{voice['ShortName']}")
    except Exception as e:
        print(f"Error listing voices: {e}")

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

def getVoiceSpeed():
    try:
        speed = input("Enter voice speed (e.g., +10%, -20%, 0%): ").strip()
        if not speed:
            return "0%" 
        if not speed.endswith("%"):
            print(f"ERROR: Speed must be in the format +10% or -10%. Using default 0%.")
            return "0%"
        return speed
    except Exception as e:
     print(f"ERROR: Failed to get voice speed: {e}")
    return "0%"

def getPitch():
    try:
        pitch = input("Enter voice pitch (e.g., +2Hz, 0Hz, -2Hz): ").strip()
        if not pitch:
            return "0Hz" 
        if not pitch.endswith("Hz"):
            print(f"ERROR: Pitch must be in the format +2Hz or -2Hz. Using default 0Hz.")
            return "0Hz"
        return pitch
    except Exception as e:
        print(f"ERROR: Failed to get voice pitch: {e}")
    return "0Hz"

async def selectEnglishVoice():
    try:
        await listEnglishVoices()
        voice = await getVoice()
        return voice
    except Exception as e:
        print(f"Error selecting voice: {e}")
        return None
    
def getText():
    try:
        text = input("Enter the text to synthesize: ")
        return text
    except Exception as e:
        print(f"Error getting text: {e}")

async def synthesize(text,voice,speed,pitch):
    try:
        tts = edge_tts.Communicate(text=text,voice=voice, rate=speed, pitch=pitch)
        await tts.save(os.path.join(DIRECTORY,OUTPUT))
    except Exception as e:
        print(f"Error synthesizing text: {e}")

async def main():
    try:
        voice = await selectEnglishVoice()
        speed = getVoiceSpeed()
        pitch = getPitch()
        text = getText()
        await synthesize(text,voice,speed,pitch)
    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    asyncio.run(main())