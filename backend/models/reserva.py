from sqlalchemy import Date, DateTime, String, Time
from sqlmodel import Field, SQLModel, Column, Integer
from pydantic import BaseModel
from datetime import date, datetime, time


class Reserva(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, autoincrement=True,
                         primary_key=True, index=True),
    )
    fecha_creacion: datetime = Field(
        sa_column=Column(DateTime, nullable=False))
    fecha: str = Field(sa_column=Column(String, nullable=False))
    hora_inicio: str = Field(sa_column=Column(String, nullable=False))
    estado: str = Field(sa_column=Column(String, nullable=False))
    personas: int = Field(sa_column=Column(Integer, nullable=False))
    usuario_id: int = Field(foreign_key="user.id")
    mesa_id: int = Field(foreign_key="table.id")


class Table(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, autoincrement=True,
                         primary_key=True, index=True),
    )
    numero: str = Field(sa_column=Column(String, nullable=False))
    capacidad: int = Field(sa_column=Column(Integer, nullable=False))


class TableCreate(BaseModel):
    numero: str
    capacidad: int


class ReservaCreate(BaseModel):
    fecha: str
    hora_inicio: str
    personas: int
    usuario_id: int


class ReservaUpdate(BaseModel):
    estado: str
    cedula: str
    fecha: str
    hora: str
    personas: int
