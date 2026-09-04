from flask import Flask, request, jsonify
import yt_dlp
import re

app = Flask(__name__)


# ==============================
# Supported platforms
# ==============================

def is_supported_url(url):
    patterns = [
        r"(youtube\.com|youtu\.be)",
        r"(facebook\.com|fb\.watch)"
    ]

    return any(re.search(pattern, url, re.IGNORECASE)
               for pattern in patterns)


# ==============================
# Format duration
# ==============================

def format_duration(seconds):
    if not seconds:
        return "Unknown"

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


# ==============================
# Extract information
# ==============================

def extract_info(url):

    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,

        # Don't download playlist videos for now
        "extract_flat": False,

        # Avoid unnecessary network requests
        "noplaylist": False,
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(url, download=False)

        # ==========================
        # Playlist
        # ==========================

        if info.get("_type") == "playlist":

            entries = []

            for item in info.get("entries", []):

                if not item:
                    continue

                entries.append({
                    "id": item.get("id"),
                    "title": item.get("title") or "Untitled",
                    "url": item.get("webpage_url")
                           or item.get("url"),
                    "thumbnail": item.get("thumbnail")
                })

            return {
                "type": "playlist",
                "title": info.get("title") or "Playlist",
                "count": len(entries),
                "entries": entries
            }

        # ==========================
        # Normal video
        # ==========================

        formats = []

        for f in info.get("formats", []):

            if not f.get("url"):
                continue

            height = f.get("height")
            width = f.get("width")

            ext = f.get("ext")
            filesize = f.get("filesize") or f.get("filesize_approx")

            # Video format
            if height:

                formats.append({
                    "format_id": f.get("format_id"),
                    "type": "video",
                    "ext": ext,
                    "height": height,
                    "width": width,
                    "fps": f.get("fps"),
                    "filesize": filesize,
                    "has_audio": bool(f.get("acodec") != "none"),
                    "has_video": bool(f.get("vcodec") != "none")
                })

            # Audio format
            elif f.get("acodec") and f.get("acodec") != "none":

                formats.append({
                    "format_id": f.get("format_id"),
                    "type": "audio",
                    "ext": ext,
                    "abr": f.get("abr"),
                    "filesize": filesize,
                    "has_audio": True,
                    "has_video": False
                })

        # Remove duplicate video qualities
        video_formats = []
        seen_heights = set()

        for f in sorted(
            formats,
            key=lambda x: x.get("height") or 0,
            reverse=True
        ):

            height = f.get("height")

            if height and height not in seen_heights:

                seen_heights.add(height)
                video_formats.append(f)

        audio_formats = [
            f for f in formats
            if f["type"] == "audio"
        ]

        return {
            "type": "video",

            "id": info.get("id"),

            "title": info.get("title")
                     or "Untitled video",

            "description": info.get("description"),

            "thumbnail": info.get("thumbnail"),

            "duration": format_duration(
                info.get("duration")
            ),

            "duration_seconds": info.get("duration"),

            "uploader": info.get("uploader"),

            "channel": info.get("channel"),

            "view_count": info.get("view_count"),

            "webpage_url": info.get("webpage_url"),

            "platform": info.get("extractor_key"),

            "formats": {
                "video": video_formats,
                "audio": audio_formats
            }
        }


# ==============================
# API: Info
# ==============================

@app.route("/api/info", methods=["GET"])
def get_info():

    url = request.args.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "URL is required"
        }), 400

    if not is_supported_url(url):
        return jsonify({
            "success": False,
            "error": "Only YouTube and Facebook URLs are supported"
        }), 400

    try:

        data = extract_info(url)

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:

        error = str(e)

        return jsonify({
            "success": False,
            "error": error
        }), 500


# ==============================
# Health check
# ==============================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "status": "online",
        "service": "Video Downloader API"
    })


# ==============================
# Local development
# ==============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
