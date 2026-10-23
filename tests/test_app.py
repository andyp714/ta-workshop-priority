from pathlib import Path

import pytest

import app as app_module
from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset task data and IDs before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"},
    ])
    app_module.next_id = 3


def test_index(client):
    """Render the task tracker with priority controls."""
    response = client.get('/')

    assert response.status_code == 200
    assert b"Task Tracker" in response.data
    assert b'id="task-priority"' in response.data
    assert b'<option value="Low">Low</option>' in response.data
    assert b'<option value="Medium" selected>Medium</option>' in response.data
    assert b'<option value="High">High</option>' in response.data


def test_get_tasks_defaults_missing_priority_to_medium(client):
    """Return Medium for existing tasks without a priority."""
    response = client.get('/api/tasks')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


def test_add_task_without_priority_defaults_to_medium(client):
    """Create a task without priority using the Medium default."""
    response = client.post('/api/tasks', json={"title": "Test new task"})

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": "Test new task",
        "priority": "Medium",
    }


def test_add_task_with_empty_priority_defaults_to_medium(client):
    """Create a task with an empty priority using the Medium default."""
    response = client.post(
        '/api/tasks',
        json={"title": "Empty priority task", "priority": ""},
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_supports_all_priorities(client, priority):
    """Create tasks with each supported priority value."""
    response = client.post(
        '/api/tasks',
        json={"title": f"{priority} task", "priority": priority},
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == priority


def test_invalid_priority_defaults_to_medium(client):
    """Create a task with an unsupported priority using Medium."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid priority task", "priority": "Urgent"},
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_priority_persists_in_get_response(client):
    """Return the created priority when tasks are retrieved."""
    client.post(
        '/api/tasks',
        json={"title": "High priority task", "priority": "High"},
    )

    response = client.get('/api/tasks')
    task = next(
        task for task in response.get_json()
        if task['title'] == 'High priority task'
    )

    assert task['priority'] == 'High'


def test_frontend_renders_priority_badges():
    """Ensure frontend rendering includes priority and its fallback."""
    project_root = Path(__file__).resolve().parents[1]
    app_script = (project_root / 'static' / 'app.js').read_text()

    assert "task.priority || 'Medium'" in app_script
    assert 'priorityBadge' in app_script
    assert 'priority-${priority.toLowerCase()}' in app_script
    assert "body: JSON.stringify({ title, priority })" in app_script


def test_add_task_missing_title(client):
    """Reject task creation requests without a title."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})

    assert response.status_code == 400
    assert "error" in response.get_json()

    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')

    assert response.status_code == 200
    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
