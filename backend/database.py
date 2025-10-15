from sqlmodel import Session, SQLModel, create_engine

import models

engine = create_engine(
    "sqlite:///task_management.db", connect_args={"check_same_thread": False}
)
# check_same_thread = False is needed for sqlite to work in a multithreaded environment


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

    session.close()
