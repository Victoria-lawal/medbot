import os, cv2, pickle, numpy as np
import time
from patient_id.model_loader import get_model

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
GALLERY_PATH = os.path.join(DATA_DIR, 'gallery.pkl')
valid_ext = ('.jpg', '.jpeg', '.png')

def load_gallery():
    if os.path.exists(GALLERY_PATH):
        with open(GALLERY_PATH, 'rb') as f:
            return pickle.load(f)
    return {}

def save_gallery(gallery):
    with open(GALLERY_PATH, 'wb') as f:
        pickle.dump(gallery, f)

def enroll_from_folder(name, folder_path):
    app = get_model()
    gallery = load_gallery()
    embeddings = []
    for fname in os.listdir(folder_path):
        if fname.startswith('.') or not fname.lower().endswith(valid_ext):
            continue
        img = cv2.imread(os.path.join(folder_path, fname))
        if img is None:
            continue
        faces = app.get(img)
        if len(faces) == 0:
            print(f"No face found in {fname}, skipping")
            continue
        embeddings.append(faces[0].normed_embedding)
    if embeddings:
        gallery[name] = np.mean(embeddings, axis=0)
        save_gallery(gallery)
        print(f"Enrolled {name} with {len(embeddings)} photos")
    else:
        print(f"Failed to enroll {name} — no usable photos")

def enroll_from_camera(name, num_shots=4, camera_index=0):
    app = get_model()
    gallery = load_gallery()
    cap = cv2.VideoCapture(camera_index)
    embeddings = []

    for i in range(num_shots):
        print(f"Capturing shot {i+1}/{num_shots} for {name} in 2 seconds...")
        time.sleep(2)
        ret, frame = cap.read()
        if not ret:
            continue
        faces = app.get(frame)
        if len(faces) == 0:
            print("No face detected, retrying this shot")
            continue
        embeddings.append(faces[0].normed_embedding)

    cap.release()

    if embeddings:
        gallery[name] = np.mean(embeddings, axis=0)
        save_gallery(gallery)
        print(f"Enrolled {name} with {len(embeddings)} shots")
    else:
        print(f"Failed to enroll {name} — no usable shots")
        
if __name__ == "__main__":
    # example: enroll_from_folder("NewPatient", "path/to/their/photos")
    pass