from abc import ABC, abstractmethod
from datetime import datetime


def parse_date(date_str):
    """Parse date string (dd/mm/yyyy)."""
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y")
    except ValueError:
        return None


def get_input(prompt, validate_fn=None):
    """Get validated input."""
    while True:
        value = input(prompt).strip()
        if not value:
            print("⚠ Cannot be empty!")
            continue
        if validate_fn and not validate_fn(value):
            print("⚠ Invalid input!")
            continue
        return value


class Task(ABC):
    """Base task class."""

    def __init__(self, title, category, priority, due_date):
        self.title = title
        self.category = category
        self.priority = priority.lower()
        self.due_date = due_date
        self.completed = False

    @abstractmethod
    def get_type(self):
        pass

    def get_time_status(self):
        """Get remaining/overdue days."""
        days = (self.due_date - datetime.now()).days
        if days > 0:
            return f"Remaining: {days} day(s)"
        if days == 0:
            return "Due today"
        return f"Overdue by {abs(days)} day(s)"

    def display(self):
        """Show task details."""
        status = "✓ Done" if self.completed else "⌛ Pending"
        print(f"\n[{self.get_type().upper()} TASK]")
        print(f"Title    : {self.title}")
        print(f"Category : {self.category}")
        print(f"Priority : {self.priority.title()}")
        print(f"Due Date : {self.due_date.strftime('%d/%m/%Y')}")
        print(f"Time Left: {self.get_time_status()}")
        print(f"Status   : {status}")


class WorkTask(Task):
    def get_type(self):
        return "work"


class PersonalTask(Task):
    def get_type(self):
        return "personal"


class TaskTracker:
    """Task management system."""

    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        print("✓ Task added successfully!")

    def view_tasks(self):
        if not self.tasks:
            print("\n⚠ No tasks available.")
            return
        print("\n===== ALL TASKS =====")
        for i, task in enumerate(self.tasks, 1):
            status = "✓ Done" if task.completed else "⌛ Pending"
            print(f"\n[{i}] {task.title}")
            print(f"    Type     : {task.get_type()}")
            print(f"    Category : {task.category}")
            print(f"    Priority : {task.priority.title()}")
            print(f"    Due Date : {task.due_date.strftime('%d/%m/%Y')}")
            print(f"    Time Left: {task.get_time_status()}")
            print(f"    Status   : {status}")

    def complete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = True
            print("✓ Task marked as completed.")
        else:
            print("⚠ Invalid task number.")

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            removed = self.tasks.pop(index)
            print(f"✓ Task deleted: {removed.title}")
        else:
            print("⚠ Invalid task number.")

    def show_progress(self):
        if not self.tasks:
            print("\n⚠ No tasks to track.")
            return
        done = sum(1 for task in self.tasks if task.completed)
        total = len(self.tasks)
        percent = (done / total) * 100
        print(f"\n📊 Progress: {done}/{total} ({int(percent)}%)")

    def view_filtered(self, task_class):
        """Show filtered tasks by type."""
        tasks = [t for t in self.tasks if isinstance(t, task_class)]
        if not tasks:
            task_name = task_class.__name__.lower().replace("task", "")
            print(f"\n⚠ No {task_name} tasks found.")
            return
        class_name = task_class.__name__.replace("Task", "").upper()
        print(f"\n===== {class_name} TASKS =====")
        for task in tasks:
            task.display()


def main():
    """Main program loop."""
    tracker = TaskTracker()
    menu = {
        "1": "Add Task",
        "2": "View All Tasks",
        "3": "Complete Task",
        "4": "Delete Task",
        "5": "Show Progress",
        "6": "View Work Tasks",
        "7": "View Personal Tasks",
        "8": "Exit",
    }

    while True:
        print("\n===== TASK TRACKER =====")
        for key, val in menu.items():
            print(f"{key}. {val}")

        choice = get_input("Enter choice: ", lambda x: x in menu)

        if choice == "1":
            task_type = get_input(
                "Task Type (Work/Personal): ",
                lambda x: x.lower() in ["work", "personal"],
            )
            title = get_input("Task Title: ")
            category = get_input("Category: ")
            priority = get_input(
                "Priority (High/Medium/Low): ",
                lambda x: x.lower() in ["high", "medium", "low"],
            )
            date_str = get_input(
                "Due Date (dd/mm/yyyy): ", lambda x: parse_date(x) is not None
            )
            due_date = parse_date(date_str)

            task = (
                WorkTask(title, category, priority, due_date)
                if task_type.lower() == "work"
                else PersonalTask(title, category, priority, due_date)
            )
            tracker.add_task(task)

        elif choice == "2":
            tracker.view_tasks()
        elif choice == "3":
            tracker.view_tasks()
            num = int(input("\nEnter task number: ")) - 1
            tracker.complete_task(num)
        elif choice == "4":
            tracker.view_tasks()
            num = int(input("\nEnter task number: ")) - 1
            tracker.delete_task(num)
        elif choice == "5":
            tracker.show_progress()
        elif choice == "6":
            tracker.view_filtered(WorkTask)
        elif choice == "7":
            tracker.view_filtered(PersonalTask)
        elif choice == "8":
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
