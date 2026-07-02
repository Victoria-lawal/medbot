import cv2
import pickle
import numpy as np
import os
from patient_id.model_loader import get_model

GALLERY_PATH = os.path.join(os.path.dirname(__file__), 'data', 'gallery.pkl')

def load_gallery():
    with open(GALLERY_PATH, 'rb') as f:
        return pickle.load(f)

def recognize(img, threshold=0.45):
    app = get_model()
    gallery = load_gallery()
    faces = app.get(img)
    results = []
    for face in faces:
        emb = face.normed_embedding
        best_name, best_score = "Unknown", -1
        for name, gal_emb in gallery.items():
            score = np.dot(emb, gal_emb)
            if score > best_score:
                best_name, best_score = name, score
        matched = best_name if best_score >= threshold else "Unknown"
        results.append({
            "matched": matched,
            "closest_name": best_name,
            "score": round(float(best_score), 3),
            "bbox": face.bbox
        })
    return results

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        print(recognize(frame))