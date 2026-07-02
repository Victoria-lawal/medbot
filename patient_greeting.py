import time
from patient_id.recognize import recognize
from patient_id.enroll import enroll_from_camera
from output.speech import say, listen_for_confirmation
from output.display import show_text

_last_seen = {"name": None, "time": 0}
COOLDOWN_SECONDS = 30

def handle_frame(img):
    results = recognize(img)
    now = time.time()

    for r in results:
        current = r["matched"]

        # Skip if we just handled this exact same outcome recently
        if current == _last_seen["name"] and (now - _last_seen["time"]) < COOLDOWN_SECONDS:
            continue

        _last_seen["name"] = current
        _last_seen["time"] = now

        if current != "Unknown":
            message = f"Hello, {current}"
            say(message)
            show_text(message)
        else:
            say("I don't recognize you. Would you like to enroll? Please say yes or no.")
            show_text("Unknown patient", "Say yes to enroll")
            confirmed = listen_for_confirmation()
            if confirmed:
                say("Enrollment starting shortly.")
                show_text("Enrollment starting")
                # enrollment flow goes here — see point 3 below
            else:
                say("Okay, not enrolling.")
                show_text("Enrollment cancelled")