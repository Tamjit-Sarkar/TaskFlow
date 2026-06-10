from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
from datetime import datetime, date

app = FastAPI()
API = "http://127.0.0.1:8000"


@app.get("/", response_class=HTMLResponse)
def home():
    tasks = requests.get(f"{API}/tasks").json()
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    pending = total - completed
    progress = int((completed / total * 100) if total else 0)

    # Ring color based on progress
    if progress == 0:
        ring_color = "#6b7280"
    elif progress < 33:
        ring_color = "#dc2626"
    elif progress < 66:
        ring_color = "#f59e0b"
    else:
        ring_color = "#10b981"

    tasks_html = ""
    for t in tasks:
        try:
            due = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
            days_left = (due - date.today()).days
        except:
            days_left = 0

        if t["completed"]:
            status = "Completed"
            status_class = "completed"
        elif days_left < 0:
            overdue_count = abs(days_left)
            status = f"Overdue by {overdue_count} day" if overdue_count == 1 else f"Overdue by {overdue_count} days"
            status_class = "overdue"
        elif days_left == 0:
            status = "Due today"
            status_class = "urgent"
        elif days_left == 1:
            status = "Due tomorrow"
            status_class = "upcoming"
        else:
            status = f"{days_left} days left"
            status_class = "normal"

        priority = t["priority"].lower()
        priority_colors = {"high": "#dc2626", "medium": "#f59e0b", "low": "#10b981"}
        priority_bg = {"high": "#fee2e2", "medium": "#fef3c7", "low": "#ecfdf5"}
        color = priority_colors.get(priority, "#666")
        bg = priority_bg.get(priority, "white")

        title_esc = t['title'].replace('"', '&quot;').replace("'", "&#39;")
        cat_esc = t['category'].replace('"', '&quot;').replace("'", "&#39;")

        tasks_html += f"""<div class="task-item {status_class}" style="background-color: {bg};">
            <a href="/complete/{t['id']}" class="checkbox {'checked' if t['completed'] else ''}">
                {'✓' if t['completed'] else ''}
            </a>
            <div class="task-main">
                <h3>{t['title']}</h3>
                <p class="task-meta">{t['category']} • {t['task_type']} • {t['due_date']}</p>
            </div>
            <span class="badge" style="background: {color}22; color: {color}; border: 1px solid {color}44;">{priority.upper()}</span>
            <span class="status">{status}</span>
            <div class="actions">
                <button onclick="openEdit({t['id']}, `{title_esc}`, `{cat_esc}`, '{priority}', '{t['due_date']}', '{t['task_type']}')" class="edit-btn">Edit</button>
                <a href="/delete/{t['id']}" class="delete-btn" onclick="return confirm('Delete?')">Delete</a>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Tamjit Taskflow</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8f7f5; color: #1a1a1a; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 60px 24px; display: grid; grid-template-columns: 1fr 300px; gap: 40px; }}
            .logo {{ position: fixed; top: 24px; left: 24px; font-weight: 700; font-size: 18px; }}
            .logo-red {{ color: #dc2626; }}
            .header {{ grid-column: 1; margin-bottom: 40px; }}
            .header h1 {{ font-size: 40px; font-weight: 300; margin-bottom: 8px; }}
            .form-card {{ grid-column: 1; background: white; padding: 30px; border-radius: 12px; margin-bottom: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
            .form-card h2 {{ font-size: 16px; margin-bottom: 20px; font-weight: 500; }}
            .form-grid {{ display: grid; gap: 12px; }}
            .form-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
            .form-row.full {{ grid-column: 1/-1; }}
            input, select {{ padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; font-family: inherit; }}
            input:focus, select:focus {{ outline: none; border-color: #1a1a1a; box-shadow: 0 0 0 3px rgba(26,26,26,0.05); }}
            .btn-submit {{ grid-column: 1/-1; padding: 10px; background: #1a1a1a; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }}
            .btn-submit:hover {{ opacity: 0.9; }}
            .tasks {{ grid-column: 1; display: flex; flex-direction: column; gap: 12px; }}
            .task-item {{ background: white; padding: 18px; border-radius: 12px; display: grid; grid-template-columns: 30px 1fr 80px 120px auto; gap: 16px; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-left: 4px solid #ddd; transition: all 0.2s; }}
            .task-item:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
            .task-item.completed {{ opacity: 0.6; }}
            .task-item.completed h3 {{ text-decoration: line-through; }}
            .task-item.urgent {{ border-left-color: #dc2626; }}
            .task-item.overdue {{ border-left-color: #dc2626; }}
            .task-item.upcoming {{ border-left-color: #f59e0b; }}
            .checkbox {{ width: 24px; height: 24px; border: 2px solid #ddd; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; text-decoration: none; color: white; font-weight: bold; transition: all 0.2s; }}
            .checkbox:hover:not(.checked) {{ border-color: #1a1a1a; }}
            .checkbox.checked {{ background: #10b981; border-color: #10b981; }}
            .task-main h3 {{ font-size: 15px; margin-bottom: 6px; }}
            .task-meta {{ font-size: 12px; color: #666; }}
            .badge {{ padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; white-space: nowrap; }}
            .status {{ font-size: 12px; font-weight: 600; color: #666; }}
            .actions {{ display: flex; gap: 8px; }}
            .edit-btn, .delete-btn {{ padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; border: none; cursor: pointer; text-decoration: none; transition: all 0.2s; }}
            .edit-btn {{ background: #f0ebe7; color: #1a1a1a; }}
            .edit-btn:hover {{ background: #ede8e2; }}
            .delete-btn {{ background: #fef2f2; color: #dc2626; }}
            .delete-btn:hover {{ background: #fee2e2; }}
            .sidebar {{ position: sticky; top: 60px; height: fit-content; }}
            .stat {{ background: white; padding: 18px; border-radius: 12px; text-align: center; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
            .stat-label {{ font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 8px; font-weight: 600; }}
            .stat-num {{ font-size: 36px; font-weight: 300; color: #1a1a1a; }}
            .progress {{ background: white; padding: 24px; border-radius: 12px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
            .progress-label {{ font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 16px; font-weight: 600; }}
            .ring {{ width: 100px; height: 100px; margin: 0 auto 12px; position: relative; }}
            .ring svg {{ width: 100%; height: 100%; transform: rotate(-90deg); }}
            .ring-bg {{ fill: none; stroke: #f0ebe7; stroke-width: 6; }}
            .ring-fill {{ fill: none; stroke: {ring_color}; stroke-width: 6; stroke-linecap: round; stroke-dasharray: 282; stroke-dashoffset: {282 - (progress/100 * 282)}; transition: stroke-dashoffset 0.5s; }}
            .progress-text {{ font-size: 24px; font-weight: 300; color: {ring_color}; }}
            .empty {{ grid-column: 1; text-align: center; padding: 60px 20px; color: #999; }}

            .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); z-index: 999; align-items: center; justify-content: center; }}
            .modal.active {{ display: flex; }}
            .modal-box {{ background: white; padding: 30px; border-radius: 12px; width: 90%; max-width: 400px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }}
            .modal-box h2 {{ margin-bottom: 20px; font-size: 18px; }}
            .modal-form {{ display: grid; gap: 12px; }}
            .modal-buttons {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }}
            .modal-btn {{ padding: 10px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; }}
            .cancel-btn {{ background: #f0ebe7; color: #1a1a1a; }}
            .save-btn {{ background: #1a1a1a; color: white; }}

            @media (max-width: 1024px) {{
                .container {{ grid-template-columns: 1fr; }}
                .sidebar {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; position: static; }}
            }}
        </style>
    </head>
    <body>
        <div class="logo">TAMJIT <span class="logo-red">TASKFLOW</span></div>

        <div class="container">
            <div>
                <div class="header">
                    <h1>Organize your work and never miss your deadline</h1>
                </div>

                <div class="form-card">
                    <h2>Add a new task</h2>
                    <form action="/add" method="post">
                        <div class="form-grid">
                            <div class="form-row full">
                                <input type="text" name="title" placeholder="Task title" required />
                            </div>
                            <div class="form-row">
                                <input type="text" name="category" placeholder="Category" required />
                                <input type="date" name="due_date" required />
                            </div>
                            <div class="form-row">
                                <select name="priority" required>
                                    <option value="">Priority</option>
                                    <option value="High">High</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Low">Low</option>
                                </select>
                                <select name="task_type" required>
                                    <option value="">Type</option>
                                    <option value="Work">Work</option>
                                    <option value="Personal">Personal</option>
                                </select>
                            </div>
                            <div class="form-row full">
                                <button type="submit" class="btn-submit">Create task</button>
                            </div>
                        </div>
                    </form>
                </div>

                <div class="tasks">
                    {tasks_html if tasks_html else '<div class="empty">No tasks yet. Create one above!</div>'}
                </div>
            </div>

            <div class="sidebar">
                <div class="stat">
                    <div class="stat-label">Total</div>
                    <div class="stat-num">{total}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Done</div>
                    <div class="stat-num">{completed}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Pending</div>
                    <div class="stat-num">{pending}</div>
                </div>
                <div class="progress">
                    <div class="progress-label">Progress</div>
                    <div class="ring">
                        <svg viewBox="0 0 100 100">
                            <circle class="ring-bg" cx="50" cy="50" r="45"></circle>
                            <circle class="ring-fill" cx="50" cy="50" r="45"></circle>
                        </svg>
                    </div>
                    <div class="progress-text">{progress}%</div>
                </div>
            </div>
        </div>

        <div id="editModal" class="modal">
            <div class="modal-box">
                <h2>Edit task</h2>
                <form id="editForm" method="POST" action="">
                    <div class="modal-form">
                        <input type="text" id="editTitle" name="title" placeholder="Title" required />
                        <input type="text" id="editCategory" name="category" placeholder="Category" required />
                        <input type="date" id="editDueDate" name="due_date" required />
                        <select id="editPriority" name="priority" required>
                            <option value="High">High</option>
                            <option value="Medium">Medium</option>
                            <option value="Low">Low</option>
                        </select>
                        <select id="editTaskType" name="task_type" required>
                            <option value="Work">Work</option>
                            <option value="Personal">Personal</option>
                        </select>
                        <div class="modal-buttons">
                            <button type="button" class="modal-btn cancel-btn" onclick="closeEdit()">Cancel</button>
                            <button type="submit" class="modal-btn save-btn">Save</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <script>
            let editId = null;

            function openEdit(id, title, category, priority, dueDate, taskType) {{
                editId = id;
                document.getElementById('editTitle').value = title;
                document.getElementById('editCategory').value = category;
                document.getElementById('editPriority').value = priority.charAt(0).toUpperCase() + priority.slice(1);
                document.getElementById('editDueDate').value = dueDate;
                document.getElementById('editTaskType').value = taskType.charAt(0).toUpperCase() + taskType.slice(1);
                document.getElementById('editForm').action = '/edit/' + id;
                document.getElementById('editModal').classList.add('active');
            }}

            function closeEdit() {{
                document.getElementById('editModal').classList.remove('active');
                editId = null;
            }}

            window.onclick = function(e) {{
                const modal = document.getElementById('editModal');
                if (e.target === modal) closeEdit();
            }}
        </script>
    </body>
    </html>"""


@app.get("/complete/{task_id}")
def complete(task_id: int):
    requests.put(f"{API}/tasks/{task_id}/complete")
    return RedirectResponse("/", 302)


@app.post("/edit/{task_id}")
def edit(task_id: int, title: str = Form(...), category: str = Form(...),
         priority: str = Form(...), due_date: str = Form(...), task_type: str = Form(...)):
    try:
        requests.put(f"{API}/tasks/{task_id}", json={
            "title": title,
            "category": category,
            "priority": priority,
            "due_date": due_date,
            "task_type": task_type
        })
    except:
        pass
    return RedirectResponse("/", 302)


@app.get("/delete/{task_id}")
def delete(task_id: int):
    requests.delete(f"{API}/tasks/{task_id}")
    return RedirectResponse("/", 302)


@app.post("/add")
def add(title: str = Form(...), category: str = Form(...),
        priority: str = Form(...), task_type: str = Form(...),
        due_date: str = Form(...)):
    requests.post(f"{API}/tasks", json={
        "title": title,
        "category": category,
        "priority": priority,
        "task_type": task_type,
        "due_date": due_date
    })
    return RedirectResponse("/", 302)