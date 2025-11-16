from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from backend.database import create_db_and_tables
from backend.routers import groups, tasks, users, workspaces
from backend.routers.tasks import scheduled_task_updates
from fastapi import FastAPI

app = FastAPI()

scheduler = BackgroundScheduler()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    # runs for every 24 hours
    # if server is down and restarted, starts fresh
    scheduler.add_job(
        scheduled_task_updates, "interval", days=1, next_run_time=datetime.now()
    )
    scheduler.start()


app.include_router(users.router, prefix="/user", tags=["user"])
app.include_router(tasks.router, prefix="/task", tags=["task"])
app.include_router(workspaces.router, prefix="/workspace", tags=["workspace"])
app.include_router(groups.router, prefix="/group", tags=["group"])
