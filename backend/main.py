from fastapi import FastAPI

from database import create_db_and_tables
from routers import tasks, users

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(users.router, prefix="/user", tags=["user"])
app.include_router(tasks.router, prefix="/task", tags=["task"])