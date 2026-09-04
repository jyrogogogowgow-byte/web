from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import re
import os


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PUBLIC_DIR = os.path.join(
    BASE_DIR,
    "public"
)


# ==========================================
# FLASK
# ==========================================

app = Flask(__name__)


# ==========================================
# SERVE WEBSITE
# ==========================================

@app.route("/")
def home():
    return send_from_directory(
        PUBLIC_DIR,
        "index.html"
    )


@app.route("/<path:filename>")
def public_files(filename):

    # Don't allow API paths to be treated
    # as static files
    if filename.startswith("api/"):
        return jsonify({
            "success": False,
            "error": "API endpoint not found"
        }), 404

    file_path = os.path.join(
        PUBLIC_DIR,
        filename
    )

    if not os.path.isfile(file_path):
        return jsonify({
            "success": False,
            "error": "File not found"
        }), 404

    return send_from_directory(
        PUBLIC_DIR,
        filename
    )


# ==========================================
# SUPPORTED URLS
# ==========================================

def is_supported_url(url):

    patterns = [

        # YouTube
        r"(https?://)?(www\.)?"
        r"(youtube\.com|youtu\.be)",

        # Facebook
        r"(https?://)?(www\.)?"
        r"(facebook\.com|fb\.watch)"

    ]

    return any(
        re.search(
            pattern,
            url,
            re.IGNORECASE
        )
        for pattern in patterns
    )


# ==========================================
# FORMAT DURATION
# ==========================================

def format_duration(seconds):

    if not seconds:
        return "00:00"

    try:
        seconds = int(seconds)
    except:
        return "00:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d}"
        )

    return (
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ==========================================
# EXTRACT VIDEO INFORMATION
# ==========================================

def extract_info(url):

    options = {

        "quiet": True,

        "no_warnings": True,

        "skip_download": True,

        # Important for playlist detection
        "extract_flat": False,

    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )


        # ==================================
        # PLAYLIST
        # ==================================

        if info.get("_type") == "playlist":

            entries = []

            for item in info.get(
                "entries",
                []
            ):

                if not item:
                    continue

                video_url = (
                    item.get("webpage_url")
                    or item.get("url")
                )

                entries.append({

                    "id":
                        item.get("id"),

                    "title":
                        item.get("title")
                        or "Untitled",

                    "url":
                        video_url,

                    "thumbnail":
                        item.get("thumbnail")

                })


            return {

                "type":
                    "playlist",

                "id":
                    info.get("id"),

                "title":
                    info.get("title")
                    or "Playlist",

                "count":
                    len(entries),

                "entries":
                    entries

            }


        # ==================================
        # NORMAL VIDEO
        # ==================================

        formats = info.get(
            "formats",
            []
        )


        video_formats = []

        audio_formats = []


        for fmt in formats:

            if not fmt.get("url"):
                continue


            vcodec = fmt.get(
                "vcodec"
            )

            acodec = fmt.get(
                "acodec"
            )

            height = fmt.get(
                "height"
            )


            # ==============================
            # VIDEO
            # ==============================

            if (
                vcodec
                and vcodec != "none"
                and height
            ):

                video_formats.append({

                    "format_id":
                        fmt.get("format_id"),

                    "ext":
                        fmt.get("ext"),

                    "height":
                        height,

                    "width":
                        fmt.get("width"),

                    "fps":
                        fmt.get("fps"),

                    "filesize":
                        (
                            fmt.get("filesize")
                            or
                            fmt.get(
                                "filesize_approx"
                            )
                        ),

                    "has_audio":
                        bool(
                            acodec
                            and
                            acodec != "none"
                        ),

                    "has_video":
                        True

                })


            # ==============================
            # AUDIO
            # ==============================

            elif (
                acodec
                and acodec != "none"
                and (
                    not vcodec
                    or vcodec == "none"
                )
            ):

                audio_formats.append({

                    "format_id":
                        fmt.get("format_id"),

                    "ext":
                        fmt.get("ext"),

                    "abr":
                        fmt.get("abr"),

                    "asr":
                        fmt.get("asr"),

                    "filesize":
                        (
                            fmt.get("filesize")
                            or
                            fmt.get(
                                "filesize_approx"
                            )
                        ),

                    "has_audio":
                        True,

                    "has_video":
                        False

                })


        # ==================================
        # REMOVE DUPLICATE VIDEO QUALITIES
        # ==================================

        unique_video_formats = []

        seen_heights = set()


        for fmt in sorted(
            video_formats,
            key=lambda x:
                x.get("height") or 0,
            reverse=True
        ):

            height = fmt.get(
                "height"
            )

            if height in seen_heights:
                continue

            seen_heights.add(
                height
            )

            unique_video_formats.append(
                fmt
            )


        # ==================================
        # RESULT
        # ==================================

        return {

            "type":
                "video",

            "id":
                info.get("id"),

            "title":
                info.get("title")
                or "Untitled video",

            "description":
                info.get("description"),

            "thumbnail":
                info.get("thumbnail"),

            "duration":
                format_duration(
                    info.get("duration")
                ),

            "duration_seconds":
                info.get("duration"),

            "uploader":
                info.get("uploader"),

            "channel":
                info.get("channel"),

            "view_count":
                info.get("view_count"),

            "webpage_url":
                info.get("webpage_url"),

            "platform":
                info.get("extractor_key"),

            "formats": {

                "video":
                    unique_video_formats,

                "audio":
                    audio_formats

            }

        }


# ==========================================
# API: HEALTH
# ==========================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success":
            True,

        "status":
            "online",

        "service":
            "MediaFlow Downloader",

        "version":
            "1.0"

    })


# ==========================================
# API: INFO
# ==========================================

@app.route(
    "/api/info",
    methods=["GET"]
)
def api_info():

    url = request.args.get(
        "url",
        ""
    ).strip()


    # Empty URL
    if not url:

        return jsonify({

            "success":
                False,

            "error":
                "Missing URL"

        }), 400


    # Unsupported website
    if not is_supported_url(url):

        return jsonify({

            "success":
                False,

            "error":
                "Only YouTube and Facebook URLs are supported"

        }), 400


    try:

        data = extract_info(
            url
        )


        return jsonify({

            "success":
                True,

            "data":
                data

        })


    except yt_dlp.utils.DownloadError as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 400


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ==========================================
# VERCEL HANDLER
# ==========================================

# Vercel detects the Flask app
# through this variable.

application = app


# ==========================================
# LOCAL DEVELOPMENT
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
