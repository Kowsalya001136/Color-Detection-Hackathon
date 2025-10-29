from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import os
import pandas as pd
import numpy as np

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Load color dataset once at startup
COLORS_DF = pd.read_csv("colors.csv")  # columns: color_name,R,G,B,HEX

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def rgb_to_hex(r, g, b):
    return "#{:02X}{:02X}{:02X}".format(int(r), int(g), int(b))

def find_closest_color_name(r, g, b):
    # Compute Euclidean distances to dataset
    rgb_arr = COLORS_DF[["R", "G", "B"]].values.astype(float)
    target = np.array([r, g, b], dtype=float)
    dists = np.linalg.norm(rgb_arr - target, axis=1)
    idx = int(np.argmin(dists))
    row = COLORS_DF.iloc[idx]
    return {
        "name": row["color_name"],
        "R": int(row["R"]),
        "G": int(row["G"]),
        "B": int(row["B"]),
        "HEX": row["HEX"]
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return redirect(url_for("index"))
    file = request.files["image"]
    if file.filename == "":
        return redirect(url_for("index"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        return redirect(url_for("show_image", filename=filename))
    return "Invalid file", 400

@app.route("/uploads/<filename>")
def show_image(filename):
    # Render the index page but instruct JS to open the image
    return render_template("index.html", image_url=url_for('static', filename=f"uploads/{filename}"))

@app.route("/get_color", methods=["POST"])
def get_color():
    """
    Expects JSON:
    {
      "filename": "example.jpg",
      "click_x": <float>,        // x coordinate in pixels relative to displayed image (or absolute)
      "click_y": <float>,        // y coordinate in pixels
      "display_width": <int>,    // displayed image width in pixels (client)
      "display_height": <int>    // displayed image height in pixels (client)
    }
    """
    data = request.get_json()
    filename = data.get("filename")
    click_x = float(data.get("click_x", 0))
    click_y = float(data.get("click_y", 0))
    display_w = float(data.get("display_width", 1))
    display_h = float(data.get("display_height", 1))

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(image_path):
        return jsonify({"error": "file not found"}), 404

    # Open image and convert to RGB
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        orig_w, orig_h = img.size

        # Map displayed coordinates -> original image coordinates
        # If the image was displayed scaled preserving aspect ratio, the client should send display width/height
        # Use ratios to map
        if display_w <= 0 or display_h <= 0:
            return jsonify({"error": "invalid display dimensions"}), 400

        x_ratio = click_x / display_w
        y_ratio = click_y / display_h

        orig_x = int(round(x_ratio * orig_w))
        orig_y = int(round(y_ratio * orig_h))

        # Clamp
        orig_x = max(0, min(orig_w - 1, orig_x))
        orig_y = max(0, min(orig_h - 1, orig_y))

        r, g, b = img.getpixel((orig_x, orig_y))

    # Find nearest color name
    nearest = find_closest_color_name(r, g, b)
    hex_code = rgb_to_hex(r, g, b)
    response = {
        "clicked_pixel": {"x": orig_x, "y": orig_y},
        "rgb": {"r": int(r), "g": int(g), "b": int(b)},
        "hex": hex_code,
        "closest_color": nearest
    }
    return jsonify(response)

if __name__ == "__main__":
    # For development; in production use a WSGI server
    app.run(host="0.0.0.0", port=8501, debug=True)
