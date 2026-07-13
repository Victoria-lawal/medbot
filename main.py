import cv2
import time
from patient_greeting import handle_frame

RECOGNITION_INTERVAL = 0.5  # seconds between recognition passes

def find_camera(candidates=(0, 1, 2)):
    for i in candidates:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Camera found at index {i}")
                return cap
            cap.release()
    return None
    
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found — check USB connection")
        return
    print("Medbot running. Ctrl+C to quit.")
    last_run = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            now = time.time()
            if now - last_run >= RECOGNITION_INTERVAL:
                handle_frame(frame)
                last_run = now
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
