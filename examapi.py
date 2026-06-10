from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")
# =========================
# DATA STORAGE
# =========================
tasks = []


# =========================
# MODEL
# =========================
class Task(BaseModel):
    title: str
    category: str
    priority: str
    due_date: str
    type: str


# =========================
# HOME PAGE
# =========================
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "examFinal.html",
        {"request": request}
    )


# =========================
# API
# =========================
@app.post("/add")
def add_task(task: Task):
    tasks.append(task.model_dump())
    return {"message": "added", "tasks": tasks}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.delete("/delete/{index}")
def delete_task(index: int):
    if 0 <= index < len(tasks):
        return tasks.pop(index)
    return {"error": "invalid index"}