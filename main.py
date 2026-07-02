import cv2
from patient_greeting import handle_frame

def main():
    cap = cv2.VideoCapture(0)
    print("Starting patient greeting loop. Press 'q' to quit.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            handle_frame(frame)
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()