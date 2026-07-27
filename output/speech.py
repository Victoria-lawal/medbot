import subprocess
import speech_recognition as sr
import json
import os
import time

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

def record_audio(filename="temp_listen.wav", duration=5):
    """Records audio via arecord (reliable) instead of PyAudio (flaky on this device)."""
    result = subprocess.run(
        ['arecord', '-D', 'plughw:CARD=sndrpigooglevoi,DEV=0',
         '-f', 'S16_LE', '-r', '16000', '-c', '1', '-d', str(duration), filename],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[DEBUG] arecord failed: {result.stderr}")
        return None
    return filename

def listen_for_confirmation(timeout=5):
    filename = record_audio(duration=timeout)
    if filename is None:
        return None

    recognizer = sr.Recognizer()
    text = None
    try:
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio).lower()
        print(f"[DEBUG] Heard: '{text}'")
    except sr.RequestError as e:
        print(f"[DEBUG] Online STT failed: {e}, switching to offline...")
        text = listen_offline_from_file(filename).lower()
        print(f"[DEBUG] Offline heard: '{text}'")
    except sr.UnknownValueError:
        print("[DEBUG] Speech detected but not understood")
        return None
    finally:
        if os.path.exists(filename):
            os.remove(filename)

    if not text:
        return None
    if "yes" in text or "yeah" in text or "confirm" in text:
        return True
    elif "no" in text or "cancel" in text:
        return False
    return None

def listen_offline_from_file(filename):
    from vosk import KaldiRecognizer
    import wave

    model = get_vosk_model()
    wf = wave.open(filename, 'rb')
    vosk_rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        vosk_rec.AcceptWaveform(data)

    result = json.loads(vosk_rec.FinalResult())
    return result.get("text", "")
