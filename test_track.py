import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from track import WorkTask, PersonalTask, TaskTracker, parse_date, get_input


# ═══════════════════════════════════════════════════════
# 1. PRIORITY TESTS - Low, Medium, High
# ═══════════════════════════════════════════════════════

class TestPriority:
    """Test all priority levels work correctly."""

    def test_high_priority(self):
        task = WorkTask("Task", "Cat", "High", datetime(2026, 6, 20))
        assert task.priority == "high"

    def test_medium_priority(self):
        task = WorkTask("Task", "Cat", "Medium", datetime(2026, 6, 20))
        assert task.priority == "medium"

    def test_low_priority(self):
        task = WorkTask("Task", "Cat", "Low", datetime(2026, 6, 20))
        assert task.priority == "low"

    def test_priority_case_insensitive(self):
        """HIGH, high, HiGh all become 'high'."""
        task1 = WorkTask("T", "C", "HIGH", datetime(2026, 6, 20))
        task2 = WorkTask("T", "C", "high", datetime(2026, 6, 20))
        task3 = WorkTask("T", "C", "HiGh", datetime(2026, 6, 20))
        assert task1.priority == "high"
        assert task2.priority == "high"
        assert task3.priority == "high"


# ═══════════════════════════════════════════════════════
# 2. DATA VALIDATION - Check data entered correctly
# ═══════════════════════════════════════════════════════

class TestDataValidation:
    """Test data validation - date parsing, input checks."""

    def test_valid_date_format(self):
        """Correct format: dd/mm/yyyy."""
        result = parse_date("15/06/2026")
        assert result == datetime(2026, 6, 15)

    def test_invalid_date_format(self):
        """Wrong format returns None."""
        assert parse_date("2026-06-15") is None
        assert parse_date("06/15/2026") is None

    def test_invalid_date_values(self):
        """Impossible dates return None."""
        assert parse_date("32/06/2026") is None  # Day too high
        assert parse_date("15/13/2026") is None  # Month too high
        assert parse_date("00/00/0000") is None

    def test_empty_date_input(self):
        """Empty string returns None."""
        assert parse_date("") is None

    @patch("builtins.input", return_value="valid_text")
    def test_valid_text_input(self, mock_input):
        """Accept non-empty input."""
        result = get_input("Enter: ")
        assert result == "valid_text"

    @patch("builtins.input", side_effect=["", "", "valid"])
    def test_reject_empty_input(self, mock_input):
        """Empty input rejected, ask again."""
        result = get_input("Enter: ")
        assert result == "valid"
        assert mock_input.call_count == 3


# ═══════════════════════════════════════════════════════
# 3. TASK TYPE - Work or Personal
# ═══════════════════════════════════════════════════════

class TestTaskType:
    """Test task types - Work vs Personal."""

    def test_work_task_type(self):
        task = WorkTask("Title", "Dev", "High", datetime(2026, 6, 20))
        assert task.get_type() == "work"

    def test_personal_task_type(self):
        task = PersonalTask("Title", "Health", "Low", datetime(2026, 6, 20))
        assert task.get_type() == "personal"

    def test_different_types_different_output(self):
        """Work and Personal return different values."""
        work = WorkTask("W", "Dev", "High", datetime(2026, 6, 20))
        personal = PersonalTask("P", "Health", "Low", datetime(2026, 6, 20))
        assert work.get_type() != personal.get_type()


# ═══════════════════════════════════════════════════════
# 4. COMPLETION STATUS - Done or Pending
# ═══════════════════════════════════════════════════════

class TestCompletionStatus:
    """Test task completion - done or pending."""

    def test_new_task_not_done(self):
        """New task starts as not done."""
        task = WorkTask("Title", "Cat", "High", datetime(2026, 6, 20))
        assert task.completed is False

    def test_mark_task_done(self):
        """Can mark task as done."""
        task = WorkTask("Title", "Cat", "High", datetime(2026, 6, 20))
        task.completed = True
        assert task.completed is True

    def test_toggle_done(self):
        """Can toggle done status."""
        task = WorkTask("Title", "Cat", "High", datetime(2026, 6, 20))
        assert task.completed is False
        task.completed = True
        assert task.completed is True
        task.completed = False
        assert task.completed is False


# ═══════════════════════════════════════════════════════
# 5. TRACKER OPERATIONS - Add, Delete, Complete
# ═══════════════════════════════════════════════════════

class TestTrackerBasic:
    """Test adding, deleting, completing tasks."""

    def test_add_one_task(self):
        tracker = TaskTracker()
        task = WorkTask("Title", "Cat", "High", datetime(2026, 6, 20))
        tracker.add_task(task)
        assert len(tracker.tasks) == 1

    def test_add_multiple_tasks(self):
        tracker = TaskTracker()
        for i in range(5):
            task = WorkTask(f"Task{i}", "Cat", "High", datetime(2026, 6, 20))
            tracker.add_task(task)
        assert len(tracker.tasks) == 5

    def test_delete_task(self):
        tracker = TaskTracker()
        task = WorkTask("Title", "Cat", "High", datetime(2026, 6, 20))
        tracker.add_task(task)
        assert len(tracker.tasks) == 1
        tracker.delete_task(0)
        assert len(tracker.tasks) == 0

    def test_complete_task_by_index(self):
        tracker = TaskTracker()
        task = WorkTask("Title", "Cat", "High", datetime(2026, 6, 20))
        tracker.add_task(task)
        tracker.complete_task(0)
        assert tracker.tasks[0].completed is True

    def test_complete_wrong_index(self):
        """Wrong index shows error."""
        tracker = TaskTracker()
        with patch("builtins.print") as mock:
            tracker.complete_task(99)
            mock.assert_called_with("⚠ Invalid task number.")

    def test_delete_wrong_index(self):
        """Delete wrong index shows error."""
        tracker = TaskTracker()
        with patch("builtins.print") as mock:
            tracker.delete_task(99)
            mock.assert_called_with("⚠ Invalid task number.")


# ═══════════════════════════════════════════════════════
# 6. PROGRESS TRACKING
# ═══════════════════════════════════════════════════════

class TestProgress:
    """Test progress calculation - how many done."""

    def test_progress_none_done(self):
        tracker = TaskTracker()
        tracker.add_task(WorkTask("T1", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(WorkTask("T2", "C", "High", datetime(2026, 6, 20)))
        done = sum(1 for t in tracker.tasks if t.completed)
        assert done == 0

    def test_progress_one_done(self):
        tracker = TaskTracker()
        tracker.add_task(WorkTask("T1", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(WorkTask("T2", "C", "High", datetime(2026, 6, 20)))
        tracker.tasks[0].completed = True
        done = sum(1 for t in tracker.tasks if t.completed)
        assert done == 1

    def test_progress_all_done(self):
        tracker = TaskTracker()
        tracker.add_task(WorkTask("T1", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(WorkTask("T2", "C", "High", datetime(2026, 6, 20)))
        for task in tracker.tasks:
            task.completed = True
        done = sum(1 for t in tracker.tasks if t.completed)
        assert done == 2

    def test_progress_percentage(self):
        """Calculate percentage correctly."""
        tracker = TaskTracker()
        tracker.add_task(WorkTask("T1", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(WorkTask("T2", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(WorkTask("T3", "C", "High", datetime(2026, 6, 20)))
        tracker.tasks[0].completed = True
        done = sum(1 for t in tracker.tasks if t.completed)
        total = len(tracker.tasks)
        percent = (done / total) * 100
        assert int(percent) == 33  # 1 of 3


# ═══════════════════════════════════════════════════════
# 7. FILTERING - Work vs Personal
# ═══════════════════════════════════════════════════════

class TestFiltering:
    """Test filtering tasks by type."""

    def test_filter_work_tasks(self):
        tracker = TaskTracker()
        tracker.add_task(WorkTask("W1", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(PersonalTask("P1", "C", "Low", datetime(2026, 6, 20)))
        tracker.add_task(WorkTask("W2", "C", "High", datetime(2026, 6, 20)))

        work = [t for t in tracker.tasks if isinstance(t, WorkTask)]
        assert len(work) == 2

    def test_filter_personal_tasks(self):
        tracker = TaskTracker()
        tracker.add_task(WorkTask("W1", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(PersonalTask("P1", "C", "Low", datetime(2026, 6, 20)))
        tracker.add_task(PersonalTask("P2", "C", "Low", datetime(2026, 6, 20)))

        personal = [t for t in tracker.tasks if isinstance(t, PersonalTask)]
        assert len(personal) == 2

    def test_filter_mixed_tasks(self):
        """Filter separates work and personal."""
        tracker = TaskTracker()
        tracker.add_task(WorkTask("W1", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(WorkTask("W2", "C", "High", datetime(2026, 6, 20)))
        tracker.add_task(PersonalTask("P1", "C", "Low", datetime(2026, 6, 20)))

        work = [t for t in tracker.tasks if isinstance(t, WorkTask)]
        personal = [t for t in tracker.tasks if isinstance(t, PersonalTask)]
        assert len(work) == 2
        assert len(personal) == 1


# ═══════════════════════════════════════════════════════
# 8. TIME STATUS - Overdue or Remaining
# ═══════════════════════════════════════════════════════

class TestTimeStatus:
    """Test time calculation - overdue or remaining days."""

    def test_overdue_task(self):
        past = datetime.now() - timedelta(days=5)
        task = WorkTask("Old", "C", "High", past)
        status = task.get_time_status()
        assert "Overdue" in status

    def test_future_task(self):
        future = datetime.now() + timedelta(days=5)
        task = WorkTask("Future", "C", "High", future)
        status = task.get_time_status()
        assert "Remaining" in status


# ═══════════════════════════════════════════════════════
# 9. TASK PROPERTIES - Title, Category, Date
# ═══════════════════════════════════════════════════════

class TestTaskProperties:
    """Test task properties store correctly."""

    def test_title_stored(self):
        task = WorkTask("My Task Title", "Dev", "High", datetime(2026, 6, 20))
        assert task.title == "My Task Title"

    def test_category_stored(self):
        task = WorkTask("Title", "Development", "High", datetime(2026, 6, 20))
        assert task.category == "Development"

    def test_due_date_stored(self):
        date = datetime(2026, 6, 20)
        task = WorkTask("Title", "C", "High", date)
        assert task.due_date == date


# ═══════════════════════════════════════════════════════
# 10. FULL WORKFLOW - User journey
# ═══════════════════════════════════════════════════════

class TestWorkflow:
    """Test complete user workflow."""

    def test_user_adds_work_task(self):
        """User adds a work task."""
        tracker = TaskTracker()
        task = WorkTask("Finish project", "Dev", "High", datetime(2026, 6, 20))
        tracker.add_task(task)
        assert len(tracker.tasks) == 1
        assert tracker.tasks[0].get_type() == "work"

    def test_user_adds_personal_task(self):
        """User adds a personal task."""
        tracker = TaskTracker()
        task = PersonalTask("Go to gym", "Health", "Medium", datetime(2026, 6, 20))
        tracker.add_task(task)
        assert len(tracker.tasks) == 1
        assert tracker.tasks[0].get_type() == "personal"

    def test_user_completes_task(self):
        """User marks task as done."""
        tracker = TaskTracker()
        tracker.add_task(WorkTask("Work", "Dev", "High", datetime(2026, 6, 20)))
        tracker.complete_task(0)
        assert tracker.tasks[0].completed is True

    def test_user_deletes_task(self):
        """User removes task."""
        tracker = TaskTracker()
        tracker.add_task(WorkTask("Work", "Dev", "High", datetime(2026, 6, 20)))
        tracker.delete_task(0)
        assert len(tracker.tasks) == 0

    def test_user_manages_multiple_tasks(self):
        """User manages multiple tasks with different priorities."""
        tracker = TaskTracker()

        # Add high priority work task
        tracker.add_task(WorkTask("Urgent work", "Dev", "High", datetime(2026, 6, 20)))

        # Add low priority personal task
        tracker.add_task(PersonalTask("Casual read", "Learning", "Low", datetime(2026, 6, 25)))

        # Add medium priority work task
        tracker.add_task(WorkTask("Regular work", "Dev", "Medium", datetime(2026, 6, 22)))

        assert len(tracker.tasks) == 3

        # Complete the high priority one
        tracker.complete_task(0)
        assert tracker.tasks[0].priority == "high"
        assert tracker.tasks[0].completed is True

        # Check progress
        done = sum(1 for t in tracker.tasks if t.completed)
        assert done == 1