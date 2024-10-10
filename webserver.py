import flask
from flask import Flask, send_file, make_response
from flask_cors import CORS
import os

app = Flask(__name__)

# Basic web server that returns files from the vod directory
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def get_file(path):
    # Construct the file path
    file_path = os.path.join("vod", path)

    # Check if the file exists
    if not os.path.isfile(file_path):
        return "File not found", 404

    # Send the file with additional headers to prevent caching and 304 responses
    try:
        response = make_response(send_file(file_path))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}", 500