import csv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CSV_FILE = 'projects.csv'

# Define the 8 specific steps requested
STEPS = [
    "Project Name",
    "Problem Statement",
    "Project Planning",
    "Backend Prototype",
    "Backend Modular",
    "Frontend Prototype",
    "Integration",
    "Testing"
]

# Build columns: Meta + (Status and Deadline for each step)
COLUMNS = ['id', 'name', 'problem', 'created_at']
for step in STEPS:
    COLUMNS.append(f"{step}_status")
    COLUMNS.append(f"{step}_deadline")

def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()

def read_projects():
    projects = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                projects.append(row)
    return projects

def write_projects(projects):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(projects)

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify(read_projects())

@app.route('/api/projects', methods=['POST'])
def add_project():
    data = request.json
    projects = read_projects()
    
    new_id = str(len(projects) + 1)
    new_project = {col: '' for col in COLUMNS}
    
    # Initialize basic info
    new_project.update({
        'id': new_id,
        'name': data.get('projectName', 'Untitled'),
        'problem': data.get('problemStatement', ''),
        'created_at': data.get('createdAt', ''),
    })
    
    # Default statuses
    for step in STEPS:
        new_project[f"{step}_status"] = "Not Started"
        new_project[f"{step}_deadline"] = "No Deadline"

    # Step 1 & 2 are usually done upon creation in this context
    new_project["Project Name_status"] = "Completed"
    new_project["Problem Statement_status"] = "Completed"
    
    projects.append(new_project)
    write_projects(projects)
    return jsonify({"message": "Project added", "project": new_project}), 201

@app.route('/api/projects/<project_id>', methods=['PATCH'])
def update_project(project_id):
    data = request.json
    projects = read_projects()
    
    found = False
    for p in projects:
        if p['id'] == project_id:
            # Update status or deadline
            if 'step' in data:
                step = data['step']
                if 'status' in data:
                    p[f"{step}_status"] = data['status']
                if 'deadline' in data:
                    p[f"{step}_deadline"] = data['deadline']
                found = True
                break
    
    if found:
        write_projects(projects)
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    initialize_csv()
    app.run(debug=True, port=5000)