import os
import shutil
from gtts import gTTS

language = 'en'
destination_dir = 'audio_files'
output_filename = 'textToSpeech.mp3'


text = input('Provide the text to convert into MP3: ')

speech = gTTS(text=text, lang=language, slow=False, tld='com.au')

speech.save(output_filename)

os.makedirs(destination_dir, exist_ok=True)

destination_path = os.path.join(destination_dir, output_filename)

shutil.move(output_filename, destination_path)

print(f"File saved to: {destination_path}")
