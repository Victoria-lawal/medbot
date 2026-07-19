import time
from collections import deque
from patient_id.recognize import recognize
from patient_id.enroll import enroll_from_camera
from patient_id.vitals import read_all_vitals
from output.speech import say, listen_for_confirmation
from output.display import show_text, show_cycling_screens

_history = deque(maxlen=5)
_last_action = {"outcome": None, "time": 0}
COOLDOWN_SECONDS = 30
STABILITY_REQUIRED = 4
_session_active = False
_prompted_this_session = False
_empty_frame_count = 0
EMPTY_FRAMES_TO_RESET = 5

def _stable_outcome():
    if len(_history) < _history.maxlen:
        return None
    counts = {}
    for name in _history:
        counts[name] = counts.get(name, 0) + 1
    best_name, best_count = max(counts.items(), key=lambda kv: kv[1])
    if best_count >= STABILITY_REQUIRED:
        return best_name
    return None

def report_vitals():
    say("Please place your hand on my left palm for a reading.")
    show_text("Reading vitals...")
    temp, bpm, spo2 = read_all_vitals(duration=10, sample_rate=25, settle_time=4)

    parts = []
    screens = []

    if temp is not None:
        parts.append(f"your temperature is {temp} degrees Celsius")
        screens.append(("Temperature", f"{temp} C"))
    if bpm is not None:
        parts.append(f"your heart rate is {bpm} beats per minute")
        screens.append(("Heart Rate", f"{bpm} bpm"))
    if spo2 is not None:
        parts.append(f"your oxygen level is {spo2} percent")
        screens.append(("SpO2", f"{spo2} %"))

    if parts:
        message = "Here are your readings: " + ", ".join(parts) + "."
        say(message)
    else:
        say("I couldn't get any clear readings. Please make sure your hand is placed firmly and try again.")
        show_text("Reading failed", "Please retry")
        return

    show_cycling_screens(screens, interval=2.5)

def handle_frame(img):
    global _session_active, _prompted_this_session, _empty_frame_count

    results = recognize(img)
    now = time.time()

    if not results:
        _empty_frame_count += 1
        if _empty_frame_count >= EMPTY_FRAMES_TO_RESET:
            _session_active = False
            _prompted_this_session = False
            _history.clear()
        return

    _empty_frame_count = 0

    if _session_active:
        return

    if not _prompted_this_session:
        say("Please look at the camera.")
        show_text("Please look at", "the camera")
        _prompted_this_session = True
        return

    _history.append(results[0]["matched"])
    outcome = _stable_outcome()
    if outcome is None:
        return

    if outcome == _last_action["outcome"] and (now - _last_action["time"]) < COOLDOWN_SECONDS:
        return

    _last_action["outcome"] = outcome
    _last_action["time"] = now
    _session_active = True

    if outcome != "Unknown":
        message = f"Hello, {outcome}"
        say(message)
        show_text(message)
        report_vitals()
    else:
        say("I don't recognize you. Would you like to enroll? Please say yes or no.")
        show_text("Unknown patient", "Say yes to enroll")
        confirmed = listen_for_confirmation()
        if confirmed:
            say("Please look at the camera. Enrollment starting shortly.")
            show_text("Enrollment starting")
            name = input("Enter patient name for enrollment: ")
            enroll_from_camera(name)
            say(f"Enrolled {name}. Thank you.")
            show_text(f"Enrolled {name}")
            _history.clear()
            report_vitals()
        else:
            say("Okay, not enrolling.")
            show_text("Enrollment cancelled")
