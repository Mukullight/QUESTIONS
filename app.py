from flask import Flask, request, render_template, redirect, url_for
from markupsafe import escape
import uuid
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
responses = {}

def load_json_categories():
    """Load all JSON files from qjson folder and extract their contents as labels"""
    qjson_folder = 'qjson'
    categories = {}
    
    if not os.path.exists(qjson_folder):
        return {"Evaluation_Settings.json": ["Open Response Form"]}
    
    try:
        # Get all JSON files in qjson folder
        json_files = sorted([f for f in os.listdir(qjson_folder) if f.endswith('.json')])
        
        for json_file in json_files:
            # Use full filename including .json extension as category name
            category_name = json_file
            
            try:
                with open(os.path.join(qjson_folder, json_file), 'r') as file:
                    data = json.load(file)
                    
                    # Extract all items from JSON as labels
                    labels = []
                    
                    if isinstance(data, dict):
                        # If it's a dictionary, use all values
                        for key, value in data.items():
                            if isinstance(value, str):
                                labels.append(value)
                            elif isinstance(value, list):
                                labels.extend([str(item) for item in value])
                            else:
                                labels.append(str(value))
                    elif isinstance(data, list):
                        # If it's a list, use all items
                        labels = [str(item) for item in data]
                    else:
                        # If it's a single value
                        labels = [str(data)]
                    
                    # Remove empty strings and duplicates while preserving order
                    labels = list(dict.fromkeys([label for label in labels if label.strip()]))
                    
                    if not labels:
                        labels = ["No items found"]
                    
                    categories[category_name] = labels
                    
                    # Initialize responses for each label
                    for label in labels:
                        if label not in responses:
                            responses[label] = []
                            
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading {json_file}: {e}")
                categories[category_name] = [f"Error loading {json_file}"]
    
    except OSError as e:
        print(f"Error accessing qjson folder: {e}")
        return {"Evaluation_Settings.json": ["Open Response Form"]}
    
    return categories if categories else {"Evaluation_Settings.json": ["Open Response Form"]}

@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("index"))

@app.route("/form", methods=["GET"])
def index():
    categories = load_json_categories()
    
    # Flatten all labels from all categories for the form
    all_labels = []
    for category_labels in categories.values():
        all_labels.extend(category_labels)
    
    response_history = {
        label: [{"id": r["id"], "text": escape(r["text"])} for r in reversed(responses.get(label, []))]
        for label in all_labels
    }
    
    return render_template("form.html", 
                         button_labels=all_labels, 
                         categories=categories,
                         response_history=response_history, 
                         modal_index=1)

@app.route("/submit/<label>", methods=["POST"])
def submit(label):
    categories = load_json_categories()
    
    # Flatten all labels from all categories
    all_labels = []
    for category_labels in categories.values():
        all_labels.extend(category_labels)
    
    if label not in all_labels:
        return render_template("form.html", 
                             button_labels=all_labels, 
                             categories=categories,
                             response_history={label: [] for label in all_labels}, 
                             modal_index=1, 
                             error="Invalid form label")
    
    user_input = request.form.get("user_input")
    if user_input:
        responses.setdefault(label, []).append({
            "id": str(uuid.uuid4()),
            "text": user_input.strip()
        })
    
    response_history = {
        label: [{"id": r["id"], "text": escape(r["text"])} for r in reversed(responses.get(label, []))]
        for label in all_labels
    }
    
    modal_index = all_labels.index(label) + 1 if label in all_labels else 1
    
    return render_template("form.html", 
                         button_labels=all_labels, 
                         categories=categories,
                         response_history=response_history, 
                         modal_index=modal_index)

if __name__ == "__main__":
    app.run(debug=True)