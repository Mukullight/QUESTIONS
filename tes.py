from flask import Flask, request, render_template, redirect, url_for
from markupsafe import escape
import uuid
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Store responses per JSON file and label
responses = {}

# Path to qjson directory
QJSON_DIR = 'qjson'

def load_button_labels(json_file):
    json_path = os.path.join(QJSON_DIR, f"{json_file}.json")
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
            if isinstance(data, list) and all(isinstance(label, str) for label in data):
                # Initialize responses for this JSON file and its labels
                if json_file not in responses:
                    responses[json_file] = {}
                for label in data:
                    if label not in responses[json_file]:
                        responses[json_file][label] = []
                return data
            else:
                return ["Open Response Form"]
    except (FileNotFoundError, json.JSONDecodeError):
        responses[json_file] = {"Open Response Form": []}
        return ["Open Response Form"]

@app.route("/", methods=["GET"])
def root():
    # Redirect to a default JSON file or a list of JSON files
    json_files = [f[:-5] for f in os.listdir(QJSON_DIR) if f.endswith('.json')]
    if json_files:
        return redirect(url_for("forms", json_file=json_files[0]))
    return render_template("forms.html", error="No JSON files found", json_file="", button_labels=[])

@app.route("/form/<json_file>", methods=["GET"])
def forms(json_file):
    button_labels = load_button_labels(json_file)
    response_history = {
        label: [{"id": r["id"], "text": escape(r["text"])} for r in reversed(responses.get(json_file, {}).get(label, []))]
        for label in button_labels
    }
    return render_template("forms.html", json_file=json_file, button_labels=button_labels, response_history=response_history, modal_index=1)

@app.route("/submit/<json_file>/<label>", methods=["POST"])
def submit(json_file, label):
    button_labels = load_button_labels(json_file)
    if label not in button_labels:
        response_history = {
            label: [] for label in button_labels
        }
        return render_template("forms.html", json_file=json_file, button_labels=button_labels, response_history=response_history, modal_index=1, error="Invalid form label")

    user_input = request.form.get("user_input")
    if user_input:
        responses.setdefault(json_file, {}).setdefault(label, []).append({
            "id": str(uuid.uuid4()),
            "text": user_input.strip()
        })

    response_history = {
        label: [{"id": r["id"], "text": escape(r["text"])} for r in reversed(responses.get(json_file, {}).get(label, []))]
        for label in button_labels
    }
    modal_index = button_labels.index(label) + 1 if label in button_labels else 1
    return render_template("forms.html", json_file=json_file, button_labels=button_labels, response_history=response_history, modal_index=modal_index)

if __name__ == "__main__":
    app.run(debug=True)