document.addEventListener('DOMContentLoaded', fetchTasks);

/** Load tasks from the backend and render them. */
async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        const taskDetails = document.createElement('span');
        const priority = task.priority || 'Medium';
        taskDetails.className = 'task-details';

        const title = document.createElement('span');
        title.textContent = task.title;

        const priorityBadge = document.createElement('span');
        priorityBadge.className = `priority priority-${priority.toLowerCase()}`;
        priorityBadge.textContent = priority;

        taskDetails.appendChild(title);
        taskDetails.appendChild(priorityBadge);

        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-btn';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        li.appendChild(taskDetails);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}

/** Create a task using the title and selected priority. */
async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();
    const priority = priorityInput.value || 'Medium';

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    titleInput.value = '';
    priorityInput.value = 'Medium';
    fetchTasks();
}

/** Delete a task and refresh the task list. */
async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
