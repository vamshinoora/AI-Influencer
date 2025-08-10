import asyncio
import edge_tts
import os
from tool import character,response


DIRECTORY = os.path.join('src','media','audio')
OUTPUT = "textToSpeech.mp3"


async def getVoice():
    try:
        voice = f"{character['voice']}"
        return voice
    except Exception as e:
        print(f"Error getting voice: {e}")
        return None

def getVoiceSpeed():
    try:
        speed = f"{character['rate']}%"
        if not speed:
            return "0%" 
        return speed
    except Exception as e:
     print(f"ERROR: Failed to get voice speed: {e}")
    return "0%"

def getPitch():
    try:
        pitch = f"{character['pitch']}Hz"
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
        voice = await getVoice()
        return voice
    except Exception as e:
        print(f"Error selecting voice: {e}")
        return None
    
def getText():
    try:
        text = response
        return text
    except Exception as e:
        print(f"Error getting text: {e}")
def getStyle():
    try:
        style = character['tone']
        return style
    except Exception as e:
        print(f"Error getting style: {e}")
        return 'neutral'

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
        style=getStyle()
        await synthesize(text,voice,speed,pitch)
    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    asyncio.run(main())