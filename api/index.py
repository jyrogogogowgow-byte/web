from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import re
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PUBLIC_DIR = os.path.join(BASE_DIR, "public")

app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory(
        PUBLIC_DIR,
        "index.html"
    )


@app.route("/<path:filename>")
def public_files(filename):
    return send_from_directory(
        PUBLIC_DIR,
        filename
    )


def is_supported_url(url):
    patterns = [
        r"(youtube\.com|youtu\.be)",
        r"(facebook\.com|fb\.watch)"
    ]

    return any(
        re.search(pattern, url, re.IGNORECASE)
        for pattern in patterns
    )


@app.route("/api/health")
def health():
    return jsonify({
        "success": True,
        "status": "online"
    })


# خلي هنا باقي كود /api/info
