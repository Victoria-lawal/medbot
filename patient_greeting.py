import time
from collections import deque
from patient_id.recognize import recognize
from patient_id.enroll import enroll_from_camera
from output.speech import say, listen_for_confirmation
from output.display import show_text

_history = deque(maxlen=5)   # last 5 frame results
_last_action = {"outcome": None, "time": 0}
COOLDOWN_SECONDS = 30
STABILITY_REQUIRED = 4       # need 4 of last 5 frames to agree

def _stable_outcome():
    """Return a name/'Unknown' only if it's the dominant result in recent history, else None."""
    if len(_history) < _history.maxlen:
        return None
    counts = {}
    for name in _history:
        counts[name] = counts.get(name, 0) + 1
    best_name, best_count = max(counts.items(), key=lambda kv: kv[1])
    if best_count >= STABILITY_REQUIRED:
        return best_name
    return None

def handle_frame(img):
    results = recognize(img)
    now = time.time()

    if not results:
        return  # no face in frame at all — don't touch history

    # Only track the first/primary detected face for stability purposes
    _history.append(results[0]["matched"])
    outcome = _stable_outcome()
    if outcome is None:
        return  # not stable yet, wait for more frames

    if outcome == _last_action["outcome"] and (now - _last_action["time"]) < COOLDOWN_SECONDS:
        return  # already handled this stable outcome recently

    _last_action["outcome"] = outcome
    _last_action["time"] = now

    if outcome != "Unknown":
        message = f"Hello, {outcome}"
        say(message)
        show_text(message)
    else:
        say("I don't recognize you. Would you like to enroll? Please say yes or no.")
        show_text("Unknown patient", "Say yes to enroll")
        confirmed = listen_for_confirmation()
        if confirmed:
            say("Please look at the camera. Enrollment starting shortly.")
            show_text("Enrollment starting")
            name = input("Enter patient name for enrollment: ")  # keyboard entry per your design
            enroll_from_camera(name)
            say(f"Enrolled {name}. Thank you.")
            show_text(f"Enrolled {name}")
            _history.clear()  # reset so newly-enrolled face gets fresh recognition
        else:
            say("Okay, not enrolling.")
            show_text("Enrollment cancelled")
from patient_id.vitals import read_vitals

def report_vitals():
    say("Please place your finger on the sensor for a reading.")
    show_text("Reading vitals...")
    bpm, spo2 = read_vitals(duration=10, sample_rate=25, settle_time=4)

    if bpm and spo2:
        message = f"Your heart rate is {bpm} beats per minute, and your oxygen level is {spo2} percent."
        say(message)
        show_text(f"HR: {bpm} bpm", f"SpO2: {spo2}%")
    elif bpm:
        say(f"Your heart rate is {bpm} beats per minute. I could not get a reliable oxygen reading.")
        show_text(f"HR: {bpm} bpm", "SpO2: unavailable")
    else:
        say("I couldn't get a clear reading. Please make sure your finger is placed firmly and try again.")
        show_text("Reading failed", "Please retry")
