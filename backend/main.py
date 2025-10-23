from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from backend.database import create_db_and_tables
from backend.routers import tasks, users
from backend.routers.tasks import scheduled_task_updates

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
