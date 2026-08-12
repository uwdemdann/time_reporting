import os
import datetime
import certifi
import polars as pl
from todoist_api_python.api import TodoistAPI

td_key = os.getenv("TODOIST_KEY")
td_api = TodoistAPI(td_key)

certifi.where()
tasks_completed = td_api.get_completed_tasks_by_completion_date(
    since = datetime.datetime(2024, 6, 1, 0, 0, 0),
    until = datetime.datetime(2024, 6, 30, 23, 59, 59)
)

task = next(tasks_completed, None)
print(f"Task: {task.content}, Completed at: {task.completed_at}")   



for task in tasks_completed:
    print(f"Task: {task.content}, Completed at: {task.completed_at}")   