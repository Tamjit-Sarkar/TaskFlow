from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

tasks = []
next_task_id = 1


class Task(BaseModel):
    title: str
    category: str
    priority: str
    due_date: str
    task_type: str


@app.get("/")
def home():
    return {"message": "API working 🚀"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.post("/tasks")
def add_task(task: Task):
    global next_task_id

    new_task = {
        "id": next_task_id,
        "title": task.title,
        "category": task.category,
        "priority": task.priority,
        "due_date": task.due_date,
        "task_type": task.task_type,
        "completed": False,
    }

    tasks.append(new_task)
    next_task_id += 1

    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    for t in tasks:
        if t["id"] == task_id:
            t["title"] = task.title
            t["category"] = task.category
            t["priority"] = task.priority
            t["due_date"] = task.due_date
            t["task_type"] = task.task_type
            return t

    return {"error": "Task not found"}


@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = True
            return t

    return {"error": "Task not found"}


@app.put("/tasks/{task_id}/uncomplete")
def uncomplete_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = False
            return t

    return {"error": "Task not found"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks

    for t in tasks:
        if t["id"] == task_id:
            tasks = [task for task in tasks if task["id"] != task_id]
            return {"message": "Task deleted"}

    return {"error": "Task not found"}