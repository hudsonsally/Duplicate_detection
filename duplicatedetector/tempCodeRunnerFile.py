from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import hashlib
import cv2

app = Flask(__name__)
FOLDER_PATH = r"C:\Users\91824\OneDrive\Desktop\duplicatedetector\videos"

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
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(os.path.join("static", os.path.basename(thumbnail_path)), frame)
    else:
        print(f"Error generating thumbnail for {video_path}")
    cap.release()

@app.route('/', methods=['GET', 'POST'])
def index():
    videos, duplicates, thumbnails = [], [], {}
    folder_path = FOLDER_PATH  # default

    if request.method == 'POST':
        # Use user-provided folder if available
        folder_path = request.form.get('folder') or FOLDER_PATH
        videos, duplicates = find_duplicate_videos(folder_path)


        for video in videos:
            video_path = os.path.join(folder_path, video)
            thumbnail_path = f"static/{video}.jpg"
            generate_thumbnail(video_path, thumbnail_path)
            thumbnails[video] = thumbnail_path

    return render_template('index.html', videos=videos, thumbnails=thumbnails, duplicates=duplicates)


@app.route('/delete_duplicates', methods=['POST'])
def delete_duplicates():
    """Delete duplicate video files from the folder."""
    _, duplicates = find_duplicate_videos(FOLDER_PATH)
    
    for file_name, _ in duplicates:
        file_path = os.path.join(FOLDER_PATH, file_name)
        os.remove(file_path)  # Delete the file

    return redirect(url_for('index'))  # Refresh the page after deletion

@app.route('/video/<filename>')
def play_video(filename):
    """Serve video files for playback."""
    return send_file(os.path.join(FOLDER_PATH, filename))

if __name__ == '__main__':
    app.run(debug=True)
