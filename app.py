from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

PRIORITIES = {"Low", "Medium", "High"}
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report", "priority": DEFAULT_PRIORITY},
    {"id": 2, "title": "Project-2 MMFs", "priority": DEFAULT_PRIORITY},
]
next_id = 3


def normalize_priority(priority):
    """Return a supported priority or the default priority."""
    if isinstance(priority, str):
        normalized_priority = priority.strip().capitalize()
        if normalized_priority in PRIORITIES:
            return normalized_priority
    return DEFAULT_PRIORITY


@app.route('/')
def index():
    """Render the task tracker page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks with a default priority when it is missing."""
    for task in tasks:
        task['priority'] = normalize_priority(task.get('priority'))
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a task with its requested or default priority."""
    global next_id
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    priority = normalize_priority(data.get('priority'))
    new_task = {
        "id": next_id,
        "title": data['title'],
        "priority": priority,
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete the task with the specified ID."""
    tasks[:] = [task for task in tasks if task['id'] != task_id]
    return jsonify({"result": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
