import flask
from flask import send_file
from flask_cors import CORS
import gunicorn

app = flask.Flask(__name__)
CORS(app)

# basic webserver that returns files from the vod directory
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def get_file(path):
    try:
        return send_file("vod/" + path)
    except FileNotFoundError:
        return "File not found", 404
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
