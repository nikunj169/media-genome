import cv2
from PIL import Image
import imagehash
import numpy as np
from numpy.linalg import norm

# -------------------------------
# Step 1: Frame Extraction
# -------------------------------
def extract_frames(video_path, sample_rate=1):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        raise ValueError("Invalid video or FPS=0")

    interval = int(fps * sample_rate)

    frames = []
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % interval == 0:
            frames.append(frame)

        frame_id += 1

    cap.release()
    return frames



# -------------------------------
# Step 2: Frame → pHash (64-dim vector)
# -------------------------------
def frame_to_phash(frame):
    # Normalize size (important for stability)
    frame = cv2.resize(frame, (256, 256))

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(frame_rgb)

    phash = imagehash.phash(pil_img)

    # Convert hex → 64-bit binary vector
    binary = np.array(
        list(map(int, bin(int(str(phash), 16))[2:].zfill(64)))
    )

    return binary


# -------------------------------
# Step 3: Video → List of hashes
# -------------------------------
def video_to_features(video_path):
    frames = extract_frames(video_path, sample_rate=0.5)

    if len(frames) == 0:
        raise ValueError("No frames extracted")

    phashes = []
    hists = []

    for frame in frames:
        phashes.append(frame_to_phash(frame))
        hists.append(frame_to_histogram(frame))

    return phashes, hists


# -------------------------------
# Step 4: Similarity (Top-K matching)
# -------------------------------
def cosine_similarity(a, b):
    denom = norm(a) * norm(b)
    if denom == 0:
        return 0.0
    return np.dot(a, b) / denom

def frame_to_histogram(frame):
    frame = cv2.resize(frame, (256, 256))

    # HSV is more stable than RGB
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    hist = cv2.calcHist([hsv], [0, 1], None, [8, 8], [0, 180, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()

    return hist

def hybrid_similarity(ph1, hist1, ph2, hist2, top_k=10):
    scores = []

    for i in range(len(ph1)):
        for j in range(len(ph2)):
            sim_phash = cosine_similarity(ph1[i], ph2[j])
            sim_hist = cosine_similarity(hist1[i], hist2[j])

            # Dynamic weighting
            if sim_hist < 0.5:
                combined = sim_phash  # ignore color (important)
            else:
                combined = 0.7 * sim_phash + 0.3 * sim_hist

            scores.append(combined)

    if len(scores) == 0:
        return 0.0

    scores.sort(reverse=True)
    return np.mean(scores[:top_k])


# -------------------------------
# Step 5: Classification
# -------------------------------
def classify_similarity(score):
    if score >= 0.75:
        return "MATCH"
    elif score >= 0.65:
        return "WEAK_MATCH"
    else:
        return "NO_MATCH"

def video_to_vector(video_path):
    """
    Converts a video into a single 64-dimensional vector
    by averaging all frame-level pHash vectors.
    This vector is used for scalable vector search (e.g., Vertex AI).
    """
    phashes, _ = video_to_features(video_path)

    if len(phashes) == 0:
        raise ValueError("No pHash features extracted from the video.")

    return np.mean(phashes, axis=0).astype(float)

# -------------------------------
# Step 6: Test Runner
# -------------------------------
if __name__ == "__main__":
    video1 = "original.mp4"
    video2 = "original_manyfilters_manytexxt.mp4"

    ph1, hist1 = video_to_features(video1)
    ph2, hist2 = video_to_features(video2)

    score = hybrid_similarity(ph1, hist1, ph2, hist2)

    print("Similarity:", score)
    print("Classification:", classify_similarity(score))