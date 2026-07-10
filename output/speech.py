import subprocess
import speech_recognition as sr
import json
import os

def say(text):
    espeak = subprocess.Popen(
        ['espeak', '-v', 'en-us', '-s', '150', '--stdout', text],
        stdout=subprocess.PIPE
    )
    aplay = subprocess.Popen(
        ['aplay', '-D', 'plughw:CARD=sndrpigooglevoi,DEV=0'],
        stdin=espeak.stdout
    )
    espeak.stdout.close()  # allow espeak to receive SIGPIPE if aplay exits early
    aplay.wait()
    espeak.wait()

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
    mic = sr.Microphone(device_index=1)
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
    recognizer.energy_threshold = 100  # much lower than default (300), tune from here
    recognizer.dynamic_energy_threshold = False  # stop auto-recalibrating upward
    mic = sr.Microphone(device_index=1)
    text = None
    try:
        with mic as source:
            print(f"[DEBUG] Energy threshold: {recognizer.energy_threshold}")
            print("Listening (online)...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
        text = recognizer.recognize_google(audio).lower()
        print(f"[DEBUG] Heard: '{text}'")
    except (sr.RequestError, ConnectionError, OSError) as e:
        print(f"[DEBUG] Online STT failed: {e}, switching to offline...")
        text = listen_offline(timeout=timeout).lower()
        print(f"[DEBUG] Offline heard: '{text}'")
    except sr.WaitTimeoutError:
        print("[DEBUG] Timed out — no speech detected in time")
        return None
    except sr.UnknownValueError:
        print("[DEBUG] Speech detected but not understood")
        return None
    if not text:
        return None
    if "yes" in text or "yeah" in text or "confirm" in text:
        return True
    elif "no" in text or "cancel" in text:
        return False
    return None
