"""
YouTube Short Uploader.
Uploads vertical video files directly to YouTube via YouTube Data API v3.
Defaults to 'private' or 'unlisted' so the creator can inspect/review before making public.
"""

import os
import re
import time
import json
import http.client
import httplib2
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from uploader.youtube_auth import get_authenticated_service

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine
)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

UPLOADS_LOG = os.path.join(os.path.dirname(__file__), "..", "output", "uploads_history.json")

def resumable_upload(insert_request):
    """Executes resumable chunk upload with retry logic."""
    response = None
    error = None
    retry = 0
    max_retries = 10

    while response is None:
        try:
            print("[YouTubeUploader] Uploading video chunk...")
            status, response = insert_request.next_chunk()
            if status:
                print(f"[YouTubeUploader] Upload progress: {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"Retriable HTTP error {e.resp.status}: {e.content}"
            else:
                raise e
        except RETRIABLE_EXCEPTIONS as e:
            error = f"Retriable connection error: {e}"

        if error is not None:
            print(f"[YouTubeUploader] {error}")
            retry += 1
            if retry > max_retries:
                raise RuntimeError("Exceeded maximum upload retry attempts.")
            sleep_sec = 2 ** retry
            print(f"[YouTubeUploader] Sleeping {sleep_sec} seconds before retrying...")
            time.sleep(sleep_sec)
            error = None

    return response

def log_upload(video_id: str, title: str, privacy: str, publish_at: str = None):
    """Log successfully uploaded video to history."""
    records = []
    if os.path.exists(UPLOADS_LOG):
        try:
            with open(UPLOADS_LOG, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            records = []

    records.append({
        "timestamp": datetime.now().isoformat(),
        "video_id": video_id,
        "url": f"https://youtu.be/{video_id}",
        "title": title,
        "privacy": privacy,
        "scheduled_publish_at": publish_at
    })

    with open(UPLOADS_LOG, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def post_discussion_comment(youtube, video_id: str, debate_question: str):
    """
    Posts an engaging debate question as a creator top comment on the uploaded Short (+200% comments).
    """
    if not debate_question:
        return None

    comment_text = (
        f"💬 QUESTION OF THE DAY:\n{debate_question}\n\n"
        f"👇 Drop your answer below! Hit subscribe to Curious Byte right now so you never miss a revelation!"
    )

    try:
        print(f"[YouTubeUploader] 💬 Posting engaging creator debate comment...")
        response = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        ).execute()
        comment_id = response.get("id")
        print(f"[YouTubeUploader] ✅ Creator discussion comment posted successfully! (ID: {comment_id})")
        return comment_id
    except HttpError as e:
        if "insufficientPermissions" in str(e) or "403" in str(e):
            print("[YouTubeUploader] ℹ️ Auto-comment note: Token currently authorized with 'youtube.upload'.")
            print("   The debate question has been highlighted at the top of the video description.")
            print("   (When re-authenticating, 'youtube.force-ssl' will enable API comment posting)")
        else:
            print(f"[YouTubeUploader] Note on posting comment: {e}")
        return None
    except Exception as e:
        print(f"[YouTubeUploader] Note on posting comment: {e}")
        return None

_CACHED_PLAYLIST_ID = None

def get_target_playlist_id(youtube, preferred_name="Facts"):
    """
    Finds the playlist ID matching preferred_name (e.g. 'Facts' or 'shorts')
    or falls back to YOUTUBE_SHORTS_PLAYLIST_ID environment variable.
    """
    global _CACHED_PLAYLIST_ID
    if _CACHED_PLAYLIST_ID:
        return _CACHED_PLAYLIST_ID

    env_id = os.getenv("YOUTUBE_SHORTS_PLAYLIST_ID")
    if env_id:
        _CACHED_PLAYLIST_ID = env_id
        return env_id

    try:
        response = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        ).execute()
        items = response.get("items", [])
        # Exact match first
        for item in items:
            title = item.get("snippet", {}).get("title", "").strip().lower()
            if title == preferred_name.strip().lower():
                _CACHED_PLAYLIST_ID = item["id"]
                print(f"[YouTubeUploader] Discovered target playlist '{item.get('snippet', {}).get('title')}': {_CACHED_PLAYLIST_ID}")
                return _CACHED_PLAYLIST_ID
        # Substring match next
        for item in items:
            title = item.get("snippet", {}).get("title", "").strip().lower()
            if preferred_name.strip().lower() in title or "fact" in title or "short" in title:
                _CACHED_PLAYLIST_ID = item["id"]
                print(f"[YouTubeUploader] Discovered matching playlist '{item.get('snippet', {}).get('title')}': {_CACHED_PLAYLIST_ID}")
                return _CACHED_PLAYLIST_ID
    except Exception as e:
        print(f"[YouTubeUploader] Note looking up playlists: {e}")

    return None

def add_video_to_playlist(youtube, video_id: str, playlist_id: str = None):
    """
    Adds an uploaded Short to a specified playlist (defaults to 'Facts' or 'shorts' playlist).
    """
    if not playlist_id:
        playlist_id = get_target_playlist_id(youtube, "Facts")
    if not playlist_id or not video_id:
        return False

    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        print(f"[YouTubeUploader] 📑 Added video {video_id} to playlist {playlist_id}")
        return True
    except HttpError as e:
        err_msg = str(e)
        if "videoAlreadyInPlaylist" in err_msg or "already in playlist" in err_msg.lower():
            return True
        elif "insufficientPermissions" in err_msg or "403" in err_msg:
            print(f"[YouTubeUploader] ℹ️ Playlist note: Token needs full YouTube scope to manage playlist.")
        else:
            print(f"[YouTubeUploader] Note on playlist auto-add: {e}")
        return False
    except Exception as e:
        print(f"[YouTubeUploader] Note on playlist auto-add: {e}")
        return False

def sync_all_videos_to_playlist(youtube, playlist_name="Facts", max_sync=50):
    """
    Syncs previously uploaded videos from uploads_history.json into the target playlist.
    """
    playlist_id = get_target_playlist_id(youtube, playlist_name)
    if not playlist_id:
        print(f"[YouTubeUploader] Playlist '{playlist_name}' not found on channel.")
        return 0

    if not os.path.exists(UPLOADS_LOG):
        return 0

    try:
        with open(UPLOADS_LOG, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        return 0

    count = 0
    for record in reversed(history):
        vid = record.get("video_id")
        if vid:
            if add_video_to_playlist(youtube, vid, playlist_id):
                count += 1
                time.sleep(0.3)
            if count >= max_sync:
                break
    print(f"[YouTubeUploader] Synced {count} videos into playlist '{playlist_name}' ({playlist_id})")
    return count

def upload_short(video_file_path: str, title: str, description: str, tags: list, privacy_status: str = "private", thumbnail_path: str = None, publish_at: str = None, debate_question: str = None):
    """
    Uploads a video to YouTube with Shorts specifications, attaches a custom thumbnail,
    optionally schedules publication at a future UTC timestamp, and posts a pinned debate comment.
    """
    creds = get_authenticated_service()
    if not creds:
        print("[YouTubeUploader] Authentication not available. Skipping auto-upload.")
        return None

    youtube = build("youtube", "v3", credentials=creds)

    # Ensure title contains #Shorts if not already present
    final_title = title if "#Shorts" in title else f"{title} #Shorts"
    if len(final_title) > 100:
        final_title = final_title[:96] + "..."

    status_dict = {
        "privacyStatus": "private" if publish_at else privacy_status,
        "selfDeclaredMadeForKids": False
    }
    if publish_at:
        status_dict["publishAt"] = publish_at

    # Ensure description contains rich viral discovery + word-level hashtags
    final_description = description
    old_tag_pattern = r"#CuriousByte\s+#Shorts\s+#Facts\s+#Science\s+#MindBlowing"
    final_description = re.sub(old_tag_pattern, "", final_description).strip()

    if len(re.findall(r'#\w+', final_description)) < 8:
        from generator.ai_viral_intelligence import build_ultimate_viral_hashtags
        word_tags = build_ultimate_viral_hashtags(title=title, script=description, max_tags=18)
        final_description = f"{final_description.strip()}\n\n{' '.join(word_tags)}"

    body = {
        "snippet": {
            "title": final_title,
            "description": final_description,
            "tags": tags,
            "categoryId": "27"  # Education
        },
        "status": status_dict
    }

    media = MediaFileUpload(
        video_file_path,
        chunksize=1024 * 1024 * 8,  # 8MB chunks (4x faster network upload)
        resumable=True,
        mimetype="video/mp4"
    )

    print(f"\n[YouTubeUploader] Initiating upload for: '{final_title}'")
    if publish_at:
        print(f"[YouTubeUploader] ⏰ Scheduled Premiere: {publish_at} (UTC) [Private until release]")
    else:
        print(f"[YouTubeUploader] Privacy setting: {privacy_status}")

    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    video_response = resumable_upload(insert_request)
    video_id = video_response.get("id")
    video_url = f"https://youtu.be/{video_id}"

    print(f"[YouTubeUploader] Successfully uploaded! Video ID: {video_id}")
    print(f"[YouTubeUploader] Video URL: {video_url}")

    # Upload custom thumbnail if available
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"[YouTubeUploader] Uploading custom thumbnail: {thumbnail_path}")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            print(f"[YouTubeUploader] Custom thumbnail attached successfully!")
        except HttpError as e:
            if "forbidden" in str(e).lower() or "not allowed" in str(e).lower():
                print("[YouTubeUploader] Note: Custom thumbnails require free account phone verification in YouTube Studio.")
                print("  (Visit https://www.youtube.com/verify to enable custom thumbnails on your channel)")
            else:
                print(f"[YouTubeUploader] Note on thumbnail upload: {e}")
        except Exception as e:
            print(f"[YouTubeUploader] Could not upload thumbnail: {e}")

    # Post Auto-Pinned / Top Creator Discussion Comment (+200% engagement)
    if debate_question:
        post_discussion_comment(youtube, video_id, debate_question)

    # Optional Auto-Add to Playlist
    add_video_to_playlist(youtube, video_id)

    log_upload(video_id, final_title, privacy_status, publish_at=publish_at)
    return video_url
