from flask import Flask, render_template
import requests

app = Flask(__name__)

BACKEND_URL = "http://127.0.0.1:8000/telemetry/latest"

@app.route("/")
def index():
    data = requests.get(BACKEND_URL).json()
    return render_template("index.html", telemetry=data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
