import os
from flask import Flask, request, jsonify
import cv2
import numpy as np

app = Flask(__name__)

def laplacian_var(img_bgr: np.ndarray) -> float:
    """Variance of Laplacian (focus metric). Higher = sharper."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Downscale huge images for stable metrics and speed
    h, w = gray.shape
    scale = 1024.0 / max(h, w) if max(h, w) > 1024 else 1.0
    if scale < 1.0:
        gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

@app.route("/")
def root():
    return "Sharpness API is live"

@app.route("/raster-quality", methods=["POST"])
def raster_quality():
    f = request.files.get("image")
    if not f:
        return jsonify({"error": "missing form-data file field 'image'"}), 400

    data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({"error": "decode_failed"}), 400

    # Optional context (not used in score, just echoed back)
    printW = float(request.form.get("printWIn", 0) or 0)
    printH = float(request.form.get("printHIn", 0) or 0)
    dpiMin = float(request.form.get("dpiMin", 0) or 0)

    score = laplacian_var(img)

    # Thresholds: tune later with your samples
    # <120 fail (soft), 120–300 warn, >300 pass (crisp)
    if score < 120:
        decision = "fail"
    elif score < 300:
        decision = "warn"
    else:
        decision = "pass"

    bullets = {
        "fail": "Raster looks soft/painty; edges lack definition.",
        "warn": "Raster slightly soft; small details may blur.",
        "pass": "Raster edges look adequately sharp."
    }

    return jsonify({
        "sharpness": {
            "lapVar": round(score, 1),
            "decision": decision,
            "bullet": bullets[decision]
        },
        "context": {
            "printWIn": printW,
            "printHIn": printH,
            "dpiMin": dpiMin
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
