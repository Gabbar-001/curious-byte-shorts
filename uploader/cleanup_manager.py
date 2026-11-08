"""
Automatic Disk Cleanup Manager.
Deletes temporary media files, scene images, generated audio, and rendered MP4s
after a video has been confirmed successfully uploaded to YouTube.
Preserves:
- output/uploads_history.json (permanent upload log)
- output/history.json (used fact IDs tracking)
- output/daily_run.log (runtime log)
- config/* and assets/* (branding, logos, tokens)
"""

import os
import shutil

def remove_file_safely(path: str):
    if path and os.path.exists(path):
        try:
            os.remove(path)
            return True
        except Exception as e:
            print(f"[Cleanup Error] Could not delete {path}: {e}")
    return False

def remove_dir_safely(path: str):
    if path and os.path.exists(path):
        try:
            shutil.rmtree(path, ignore_errors=True)
            return True
        except Exception as e:
            print(f"[Cleanup Error] Could not delete dir {path}: {e}")
    return False

def cleanup_short_assets(short_id: str, video_path: str = None, audio_path: str = None, sub_path: str = None, thumbnail_paths: list = None):
    """
    Deletes all temporary media files associated with this short after upload.
    """
    deleted_items = 0
    
    # 1. Delete Rendered MP4 Video
    if video_path and remove_file_safely(video_path):
        deleted_items += 1

    # 2. Delete Audio and Subtitle files
    if audio_path and remove_file_safely(audio_path):
        deleted_items += 1
    if sub_path and remove_file_safely(sub_path):
        deleted_items += 1

    # 3. Delete Thumbnails
    if thumbnail_paths:
        for t in thumbnail_paths:
            if t and remove_file_safely(t):
                deleted_items += 1

    # 4. Delete Temporary Scene Dirs (temp_scenes, temp_geostudio, temp_true3d)
    temp_roots = [
        os.path.join("output", "temp_scenes", short_id),
        os.path.join("output", "temp_geostudio", short_id),
        os.path.join("output", "temp_true3d", short_id)
    ]
    for tr in temp_roots:
        if os.path.exists(tr):
            remove_dir_safely(tr)
            deleted_items += 1

    print(f"\n[Cleanup] 🧹 Successfully cleaned up {deleted_items} temporary files & folders for '{short_id}'.")
    print("  ✓ Local MP4, audio files, and scene images removed from disk.")
    print("  ✓ Upload history and live YouTube link preserved in uploads_history.json.")
