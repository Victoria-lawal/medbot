import subprocess
import speech_recognition as sr
import json
import os

def say(text, voice="en+f3", speed=150):
    espeak = subprocess.Popen(
        ['espeak', '-v', voice, '-s', str(speed), '--stdout', text],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    aplay = subprocess.Popen(
        ['aplay', '-D', 'plughw:CARD=sndrpigooglevoi,DEV=0'],
        stdin=espeak.stdout,
        stderr=subprocess.DEVNULL
    )
    espeak.stdout.close()
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
    mic = sr.Microphone(device_index=0)
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

def listen_for_confirmation(timeout=5, retries=2):
    for attempt in range(retries):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 100
        recognizer.dynamic_energy_threshold = False
        try:
            mic = sr.Microphone(device_index=0, sample_rate=48000, chunk_size=1024)
            with mic as source:
                print(f"[DEBUG] Energy threshold: {recognizer.energy_threshold}")
                print("Listening (online)...")
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            text = recognizer.recognize_google(audio).lower()
            print(f"[DEBUG] Heard: '{text}'")
        except (sr.RequestError, ConnectionError, OSError) as e:
            print(f"[DEBUG] Online STT failed: {e}, switching to offline...")
            try:
                text = listen_offline(timeout=timeout).lower()
                print(f"[DEBUG] Offline heard: '{text}'")
            except Exception as offline_e:
                print(f"[DEBUG] Offline STT also failed: {offline_e}")
                continue
        except sr.WaitTimeoutError:
            print("[DEBUG] Timed out — no speech detected in time")
            return None
        except sr.UnknownValueError:
            print("[DEBUG] Speech detected but not understood")
            return None
        except Exception as e:
            print(f"[DEBUG] Mic error (attempt {attempt+1}/{retries}): {e}")
            time.sleep(0.5)
            continue

        if not text:
            return None
        if "yes" in text or "yeah" in text or "confirm" in text:
            return True
        elif "no" in text or "cancel" in text:
            return False
        return None

    print("[DEBUG] All retry attempts failed")
    return None
