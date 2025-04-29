import os
import time
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from typing import Annotated
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Intentar conectarse a la base de datos con reintentos


def connect_to_database_with_retries(retries: int = 10, delay: int = 5):
    for attempt in range(retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Probar la conexión
            with engine.connect() as connection:
                print("Conexión exitosa a la base de datos.")
            return engine
        except OperationalError as e:
            print(
                f"Intento {attempt + 1} de {retries}: No se pudo conectar a la base de datos. Reintentando en {delay} segundos...")
            time.sleep(delay)
    raise Exception(
        "No se pudo conectar a la base de datos después de varios intentos.")


# Crear el motor de la base de datos
engine = connect_to_database_with_retries()


def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)  # Reestablecer la base de datos
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
