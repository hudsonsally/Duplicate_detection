from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import hashlib
import cv2
import shutil

app = Flask(__name__)
FOLDER_PATH = r"C:\Users\91824\Downloads\duplicatedetector\videos"
MOVED_FOLDER = r"C:\Users\91824\Downloads\duplicatedetector\moved duplicates"

# Create necessary directories
os.makedirs(FOLDER_PATH, exist_ok=True)
os.makedirs(MOVED_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

def get_file_hash(file_path):
    """Generate SHA256 hash for a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicate_videos(folder_path):
    """Find duplicate video files in the given folder."""
    hashes = {}
    duplicates = []
    all_videos = []

    if not os.path.exists(folder_path):
        return [], []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isfile(file_path) and file_name.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            file_hash = get_file_hash(file_path)
            all_videos.append(file_name)

            if file_hash in hashes:
                duplicates.append((file_name, hashes[file_hash]))
            else:
                hashes[file_hash] = file_name
    
    return all_videos, duplicates

def generate_thumbnail(video_path, thumbnail_path):
    """Extract the first frame of a video for thumbnail."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open {video_path}")
        return None
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(thumbnail_path, frame)
        return thumbnail_path
    else:
        print(f"Error generating thumbnail for {video_path}")
        return None
    cap.release()

@app.route('/', methods=['GET', 'POST'])
def index():
    videos, duplicates, thumbnails = [], [], {}
    folder_path = FOLDER_PATH  # default

    if request.method == 'POST':
        # Use user-provided folder if available
        folder_path = request.form.get('folder') or FOLDER_PATH

        if not os.path.exists(folder_path):
            return render_template('index.html', error="Folder not found", videos=[], thumbnails={}, duplicates=[])

        videos, duplicates = find_duplicate_videos(folder_path)
        for video in videos:
            video_path = os.path.join(folder_path, video)
            thumbnail_path = os.path.join("static", f"{video}.jpg")
            thumb = generate_thumbnail(video_path, thumbnail_path)
            thumbnails[video] = thumb

    return render_template('index.html', videos=videos, thumbnails=thumbnails, duplicates=duplicates)

@app.route('/delete_duplicates', methods=['POST'])
def delete_duplicates():
    """Move duplicate video files to the 'moved duplicates' folder."""
    _, duplicates = find_duplicate_videos(FOLDER_PATH)
    
    for file_name, _ in duplicates:
        file_path = os.path.join(FOLDER_PATH, file_name)
        if os.path.exists(file_path):
            moved_path = os.path.join(MOVED_FOLDER, file_name)
            shutil.move(file_path, moved_path)

    return redirect(url_for('index'))

@app.route('/video/<filename>')
def play_video(filename):
    """Serve video files for playback."""
    video_path = os.path.join(FOLDER_PATH, filename)
    if os.path.exists(video_path):
        return send_file(video_path)
    return "Video not found", 404

if __name__ == '__main__':
    app.run(debug=True)
