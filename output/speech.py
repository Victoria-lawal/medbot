import subprocess
import speech_recognition as sr
import json
import os

def say(text):
    espeak = subprocess.Popen(
        ['espeak', '-v', 'en-us', '-s', '150', '--stdout', text],
        stdout=subprocess.PIPE
    )
    subprocess.run(
        ['aplay', '-D', 'plughw:CARD=sndrpigooglevoi,DEV=0'],
        stdin=espeak.stdout
    )
    espeak.stdout.close()

def get_vosk_model():
    from vosk import Model
    global _vosk_model
    _vosk_model = None
    if _vosk_model is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk-model-small-en-us-0.15')
        _vosk_model = Model(model_path)
    return _vosk_model

def listen_offline(timeout=5):
    from vosk import KaldiRecognizer
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    model = get_vosk_model()
    vosk_rec = KaldiRecognizer(model, 16000)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening (offline mode)...")
        audio = recognizer.listen(source, timeout=timeout)
    raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
    vosk_rec.AcceptWaveform(raw_data)
    result = json.loads(vosk_rec.FinalResult())
    return result.get("text", "")

def listen_for_confirmation(timeout=5):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    text = None
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening (online)...")
            audio = recognizer.listen(source, timeout=timeout)
        text = recognizer.recognize_google(audio).lower()
    except (sr.RequestError, ConnectionError, OSError):
        print("Online STT unavailable, switching to offline...")
        text = listen_offline(timeout=timeout).lower()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return None
    if not text:
        return None
    if "yes" in text or "yeah" in text or "confirm" in text:
        return True
    elif "no" in text or "cancel" in text:
        return False
    return None
