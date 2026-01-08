import csv
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# -------------------- App Setup --------------------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

CSV_FILE = "projects.csv"

# Default steps for new projects
DEFAULT_STEPS = [
    {"name": "Project Name", "status": "Completed", "deadline": ""},
    {"name": "Problem Statement", "status": "Completed", "deadline": ""},
    {"name": "Project Planning", "status": "Not Started", "deadline": ""},
    {"name": "Backend Prototype", "status": "Not Started", "deadline": ""},
    {"name": "Backend Modular", "status": "Not Started", "deadline": ""},
    {"name": "Frontend Prototype", "status": "Not Started", "deadline": ""},
    {"name": "Integration", "status": "Not Started", "deadline": ""},
    {"name": "Testing", "status": "Not Started", "deadline": ""}
]

COLUMNS = ["id", "name", "problem", "created_at", "steps"]

# -------------------- CSV Helpers --------------------
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()

def read_projects():
    projects = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Deserialize the steps JSON string back into a list
                try:
                    row["steps"] = json.loads(row["steps"])
                except:
                    row["steps"] = []
                projects.append(row)
    return projects

def write_projects(projects):
    # Prepare data for CSV by serializing steps to JSON strings
    formatted_projects = []
    for p in projects:
        copy_p = p.copy()
        if isinstance(copy_p["steps"], list):
            copy_p["steps"] = json.dumps(copy_p["steps"])
        formatted_projects.append(copy_p)
        
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(formatted_projects)

initialize_csv()

# -------------------- Routes --------------------
@app.route("/api/projects", methods=["GET"])
def get_projects():
    return jsonify(read_projects())

@app.route("/api/projects", methods=["POST"])
def add_project():
    data = request.json or {}
    projects = read_projects()

    # Generate a simple ID
    new_id = str(max([int(p["id"]) for p in projects]) + 1) if projects else "1"
    
    new_project = {
        "id": new_id,
        "name": data.get("projectName", "Untitled"),
        "problem": data.get("problemStatement", ""),
        "created_at": data.get("createdAt", ""),
        "steps": DEFAULT_STEPS.copy()
    }

    projects.append(new_project)
    write_projects(projects)

    return jsonify({"message": "Project added", "project": new_project}), 201

@app.route("/api/projects/<project_id>", methods=["PATCH"])
def update_project(project_id):
    data = request.json or {}
    projects = read_projects()

    for p in projects:
        if p["id"] == project_id:
            # If the entire steps array is provided (for adding/deleting steps)
            if "steps" in data:
                p["steps"] = data["steps"]
            
            # If a specific step is being updated (status/deadline)
            elif "stepIndex" in data:
                idx = int(data["stepIndex"])
                if 0 <= idx < len(p["steps"]):
                    if "status" in data:
                        p["steps"][idx]["status"] = data["status"]
                    if "deadline" in data:
                        p["steps"][idx]["deadline"] = data["deadline"]

            write_projects(projects)
            return jsonify({"success": True, "project": p})

    return jsonify({"error": "Project not found"}), 404

@app.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    projects = read_projects()
    updated_projects = [p for p in projects if p["id"] != project_id]

    if len(projects) == len(updated_projects):
        return jsonify({"error": "Project not found"}), 404

    write_projects(updated_projects)
    return jsonify({"message": "Project deleted successfully"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)