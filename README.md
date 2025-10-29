# Color Detection from Images — Hackathon Level-2

## Overview
This project is a simple web application that allows users to upload an image, click anywhere on the displayed image, and get:

- RGB values of the clicked pixel
- HEX code
- Closest color name from `colors.csv`
- A color-filled box as reference

Backend: Flask (Python)  
Frontend: HTML + JavaScript (no frameworks)

## Files
- `app.py` — Flask backend
- `templates/index.html` — Web UI
- `static/uploads/` — Uploaded images stored here
- `colors.csv` — Color dataset (color_name, R, G, B, HEX)
- `requirements.txt` — Python dependencies

## Setup (local)
1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS / Linux
   venv\Scripts\activate           # Windows
