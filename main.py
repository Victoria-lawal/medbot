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
    cap = find_camera()
    if cap is None:
        print("Camera not found — check USB connection")
        return
    print("Medbot running. Ctrl+C to quit.")
    last_run = 0
    
    # Warm up camera buffer
    for _ in range(5):
        cap.read()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Warning: Failed to grab frame from camera")
                time.sleep(0.1)
                continue

            now = time.time()
            if now - last_run >= RECOGNITION_INTERVAL:
                print("[DEBUG] Processing frame...")
                handle_frame(frame, cap)
                print("[DEBUG] Frame processed successfully.")
                last_run = now

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
