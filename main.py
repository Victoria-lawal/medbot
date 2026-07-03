import cv2
from patient_greeting import handle_frame

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found — check USB connection")
        return
    print("Medbot running. Ctrl+C to quit.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            handle_frame(frame)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()