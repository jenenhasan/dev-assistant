import speech_recognition as sr
import pyttsx3
import langid
from gtts import gTTS
import os
import sys
import warnings
import subprocess
import time 



# Kill Rhythmbox if running (silently)
os.system("pkill -f rhythmbox 2>/dev/null")

os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.filterwarnings("ignore", module="pyttsx3")

class VoiceControl:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init(driverName="espeak")
    
        
    
        self._setup_voices()
        self.lang_for_speech = 'en'
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300 # Adjust as needed
        self.channel = None
        

    def _setup_voices(self):
        voices = self.engine.getProperty('voices')
        self.english_voice = voices[1].id  # Verify index for your system
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('voice', self.english_voice)

    def speak(self, text, language='en'):
        print(f"Speaking in {language}: {text}")
        
        tts = gTTS(text=text, lang=language)
        tts.save("temp.mp3")
        self._play_audio()

    def _play_audio(self):
        if sys.platform == "win32":
            os.system("start /wait temp.mp3")
            time.sleep(5)
            os.remove("temp.mp3")
        elif sys.platform == "darwin":
           subprocess.call(["afplay", "temp.mp3"])
           os.remove("temp.mp3")
        else:  # Linux
           subprocess.call(["xdg-open", "temp.mp3"])
           time.sleep(5)
           os.remove("temp.mp3")

    def _detect_language(self, audio):
        try:
            raw_text = self.recognizer.recognize_google(audio, language='tr')
            lang, confidence = langid.classify(raw_text)
            return 'tr' if lang == 'tr' and confidence > 0.3 else 'en'
        except Exception:
            return 'en'

    def listen(self  , phrase_time_limit=30):
        try:
            with sr.Microphone() as mic:
                self.recognizer.adjust_for_ambient_noise(mic, duration=2)
                print("Listening...")
                audio = self.recognizer.listen(mic , timeout=phrase_time_limit)
                print("Recognizing...")
                
                #self.lang_for_speech = self._detect_language(audio)
                language_code = 'tr-TR' if self.lang_for_speech == 'tr' else 'en-US'
                text = self.recognizer.recognize_google(audio, language=language_code)
                print("Recognized:", text)
                return text
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that.", self.lang_for_speech)
        except sr.RequestError:
            self.speak("Sorry, there was an error with the speech recognition service.", self.lang_for_speech)
        except Exception as e:
            self.speak(f"An error occurred: {str(e)}", self.lang_for_speech)
        return None
    def speak_random(self , text_list):
        import random
        text = random.choice(text_list)
        self.speak(text, self.lang_for_speech)

   
   
    
    def register_command(self, trigger_words, action):
        if not hasattr(self, 'commands'):
            self.commands = {}
        for word in trigger_words:
            self.commands[word.lower()] = action

    def run(self):
        while True:
            text = self.listen()
            if text:
                self.speak("Getting the Response", self.lang_for_speech)

if __name__ == "__main__":
    vc = VoiceControl()
    vc.run()