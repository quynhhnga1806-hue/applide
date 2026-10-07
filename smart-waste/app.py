"""SMART WASTE - Flask backend.

Chạy ứng dụng:
    python app.py

API chính:
    POST /api/classify - nhận multipart/form-data với field "image"
"""

from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from model_ai import ALLOWED_LABELS, classify_image


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.config["JSON_SORT_KEYS"] = False


def is_allowed_file(filename: str) -> bool:
    """Chỉ cho phép JPG, JPEG và PNG."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "smart-waste"})


@app.get("/manus-routes.json")
def routes_manifest():
    """Route manifest dùng cho preview và kiểm tra cấu trúc website."""
    return jsonify(
        {
            "routes": [
                {"path": "/", "title": "SMART WASTE – Phân loại rác thông minh"}
            ]
        }
    )


@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify({"success": False, "message": "Ảnh quá lớn. Vui lòng chọn ảnh dưới 10 MB."}), 413


@app.post("/api/classify")
def classify():
    """Lưu ảnh tạm thời, đưa vào model AI và trả kết quả JSON."""
    image_file = request.files.get("image")

    if image_file is None or image_file.filename == "":
        return jsonify({"success": False, "message": "Vui lòng chọn hoặc chụp một ảnh rác."}), 400

    if not is_allowed_file(image_file.filename):
        return jsonify({"success": False, "message": "Định dạng không hợp lệ. Chỉ hỗ trợ JPG, JPEG và PNG."}), 400

    safe_name = secure_filename(image_file.filename)
    extension = safe_name.rsplit(".", 1)[1].lower()
    stored_name = f"{uuid4().hex}.{extension}"
    stored_path = UPLOAD_DIR / stored_name
    image_file.save(stored_path)

    try:
        result = classify_image(stored_path)
    except Exception as error:  # Không để lỗi model làm hỏng trải nghiệm demo.
        app.logger.exception("AI classification failed: %s", error)
        result = {
            "label": "Rác khác",
            "confidence": 50.0,
            "bin": "THÙNG RÁC KHÁC",
            "guidance": "Hãy kiểm tra lại vật thể và phân loại theo hướng dẫn tại địa phương.",
            "icon": "◌",
            "accent": "other",
            "is_fallback": True,
        }

    return jsonify(
        {
            "success": True,
            "filename": safe_name,
            "image_url": f"/static/uploads/{stored_name}",
            "supported_labels": ALLOWED_LABELS,
            **result,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
