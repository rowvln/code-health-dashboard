from pathlib import Path
from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename
from ..services.analyzer import analyze_path

analysis_bp = Blueprint("analysis", __name__)
ALLOWED_EXTENSIONS = {"py", "zip"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@analysis_bp.post("/analyze")
def analyze_code():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(uploaded_file.filename):
        return jsonify({"error": "Only .py and .zip files are supported in the MVP."}), 400

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    filename = secure_filename(uploaded_file.filename)
    file_path = upload_folder / filename
    uploaded_file.save(file_path)

    result = analyze_path(file_path)
    return jsonify(result)
