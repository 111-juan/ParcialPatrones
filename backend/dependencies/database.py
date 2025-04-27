import os
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from typing import Annotated
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)  # Reestablecer la base de datos
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
