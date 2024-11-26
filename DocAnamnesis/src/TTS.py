from gtts import gTTS
import io

def generate_audio(text=""):
    tts = gTTS(text=text, lang='en')
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file