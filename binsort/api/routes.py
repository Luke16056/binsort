"""API: gets the photo (or typed text), sends back the results as JSON.

Interface:
    GET  /          the web page (BinSort App)
    POST /sort      form field "photo" (file) or "text"
    POST /feedback  JSON {"result": {...one item...}, "ok": true/false}
"""
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from binsort.bin_rules import BinRules
from binsort.database import Database
from binsort.feedback import Feedback
from binsort.item_detector import get_detector
from binsort.photo_prep import BadPhoto, prepare
from binsort.sorting import Sorter

DEFAULT_DB = Path(__file__).resolve().parents[2] / "binsort.db"


def create_app(detector=None, db_path=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

    # Wire the layers together once, here. Nothing else creates components.
    db = Database(db_path or os.environ.get("BINSORT_DB", DEFAULT_DB))
    sorter = Sorter(prepare, detector or get_detector(), BinRules(db))
    feedback = Feedback(db)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/sort")
    def sort():
        photo = request.files.get("photo")
        try:
            if photo and photo.filename:
                return jsonify(sorter.sort(photo.read()))
            return jsonify(sorter.sort_text(request.form.get("text", "")))
        except BadPhoto as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/feedback")
    def give_feedback():
        data = request.get_json(silent=True) or {}
        try:
            feedback.report(data.get("result"), data.get("ok"))
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify({"saved": True})

    @app.errorhandler(413)
    def too_big(_error):
        return jsonify({"error": "The photo is too big. Please use one under 10 MB."}), 413

    return app
