from datetime import date, datetime, time
from fastapi import APIRouter, HTTPException
from sqlalchemy import Time, cast
from sqlmodel import select

from dependencies.database import SessionDep
from models.api_response import APIResponse
from models.reserva import Reserva, ReservaCreate, ReservaUpdate, Table, TableCreate
from models.user import User

router = APIRouter(prefix="/reservas")


@router.post("/create/table/")
def create_table(table: TableCreate, session: SessionDep) -> APIResponse:
    # Crear la mesa
    table_db = Table(
        numero=table.numero,
        capacidad=table.capacidad,
    )
    session.add(table_db)
    session.commit()
    session.refresh(table_db)

    return APIResponse(
        code=201,
        status="success",
        message="Table created successfully",
        data={"table": table_db},
    )


@router.get("/tables/")
def get_tables(session: SessionDep) -> APIResponse:
    tables = session.exec(select(Table)).all()
    if not tables:
        raise HTTPException(status_code=404, detail="No tables found")

    return APIResponse(
        code=200,
        status="success",
        message="Tables retrieved successfully",
        data={"tables": tables},
    )


@router.post("/create/")
def create_reserva(reserva: ReservaCreate, session: SessionDep) -> APIResponse:
    print(reserva)
    # Obtener la mesa con la capacidad requerida
    mesa = select_table(reserva.personas, reserva.fecha,
                        reserva.hora_inicio, session)
    if not mesa:
        raise HTTPException(status_code=404, detail="No available table found")
    # Crear la reserva

    reserva_db = Reserva(
        fecha_creacion=datetime.now(),
        fecha=reserva.fecha,
        hora_inicio=reserva.hora_inicio,
        estado="activa",
        personas=reserva.personas,
        usuario_id=reserva.usuario_id,
        mesa_id=mesa.id,
    )

    session.add(reserva_db)
    session.commit()
    session.refresh(reserva_db)

    # Obtener nombre y cedula del usuario
    user = session.exec(select(User.name, User.cedula).where(
        User.id == reserva.usuario_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return APIResponse(
        code=201,
        status="success",
        message="Reserva created successfully",
        data={
            "reserva": {
                "id": reserva_db.id,
                "fecha_creacion": reserva_db.fecha_creacion,
                "fecha": reserva_db.fecha,
                "hora": reserva_db.hora_inicio,
                "personas": reserva_db.personas,
                "estado": reserva_db.estado,
            },
            "mesa": {
                "numero": mesa.numero,
                "capacidad": mesa.capacidad,
            },
            "usuario": {
                "id": reserva_db.usuario_id,
                "nombre": user.name,
                "cedula": user.cedula,
            },
        },
    )


def select_table(capacidad: int, fecha: str, hora: str, session: SessionDep, mesa_id: int | None = None):
    # Obtener la mesa con la capacidad requerida
    mesas = session.exec(
        select(Table).where(Table.capacidad >=
                            capacidad)
    ).all()

    if not mesas:
        raise HTTPException(status_code=404, detail="No available table found")

    # Ver que no tengan reservas activas a esta hora
    reservas = session.exec(
        select(Reserva).where(
            Reserva.fecha == fecha,
            Reserva.hora_inicio == hora,
            Reserva.estado == "activa",
        )
    ).all()
    mesas_reservadas = [reserva.mesa_id for reserva in reservas]

    mesas = [
        mesa for mesa in mesas if mesa.id not in mesas_reservadas or mesa.id == mesa_id]
    if not mesas:
        raise HTTPException(status_code=404, detail="No available table found")

    # Si hay mesas disponibles, seleccionar la más cercana a la capacidad requerida
    min_diferencia = 0
    mesa_seleccionada = None
    for mesa in mesas:
        # Si la diferencia es exacta, seleccionar la mesa y salir del bucle
        if mesa.capacidad == capacidad:
            mesa_seleccionada = mesa.numero
            break
        diferencia = mesa.capacidad - capacidad
        # Si no hay mesa exacta, seleccionar la más cercana
        if diferencia >= 0 and (mesa_seleccionada is None or diferencia < min_diferencia):
            min_diferencia = diferencia
            mesa_seleccionada = mesa.numero
    if mesa_seleccionada:
        mesa = session.get(Table, mesa_seleccionada)
        return mesa
    else:
        raise HTTPException(status_code=404, detail="No available table found")


@router.get("/")
def get_reservas_activas(session: SessionDep) -> APIResponse:
    reservas = session.exec(select(Reserva)).all()
    if not reservas:
        raise HTTPException(status_code=404, detail="No reservations found")

    reservas_data = []
    for reserva in reservas:
        # Obtener nombre y cedula del usuario
        user = session.exec(select(User.name, User.cedula, User.phone).where(
            User.id == reserva.usuario_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Obtener la mesa con la capacidad requerida
        mesa = session.exec(select(Table).where(
            Table.id == reserva.mesa_id)).first()
        if not mesa:
            raise HTTPException(status_code=404, detail="Table not found")

        reservas_data.append({
            "reserva": {
                "id": reserva.id,
                "fecha_creacion": reserva.fecha_creacion,
                "fecha": reserva.fecha,
                "hora_inicio": reserva.hora_inicio,
                "estado": reserva.estado,
                "personas": reserva.personas,
            },
            "mesa": {
                "numero": mesa.numero,
                "capacidad": mesa.capacidad,
            },
            "usuario": {
                "id": reserva.usuario_id,
                "nombre": user.name,
                "cedula": user.cedula,
                "telefono": user.phone,
            },
        })

    return APIResponse(
        code=200,
        status="success",
        message="Reservations retrieved successfully",
        data={"reservas": reservas_data},
    )


@router.get("/{reserva_id}")
def get_reserva(reserva_id: int, session: SessionDep) -> APIResponse:
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return APIResponse(
        code=200,
        status="success",
        message="Reservation retrieved successfully",
        data={"reserva": reserva},
    )


@router.get("/user/{user_id}/")
def get_reservas_by_user(user_id: int, session: SessionDep) -> APIResponse:
    reservas = session.exec(
        select(Reserva).where(Reserva.usuario_id == user_id)).all()
    if not reservas:
        raise HTTPException(
            status_code=404, detail="No reservations found for this user")

    reservas_data = []
    for reserva in reservas:
        # Obtener nombre y cedula del usuario
        user = session.exec(select(User.name, User.cedula).where(
            User.id == reserva.usuario_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Obtener la mesa con la capacidad requerida
        mesa = session.exec(select(Table).where(
            Table.id == reserva.mesa_id)).first()
        if not mesa:
            raise HTTPException(status_code=404, detail="Table not found")

        reservas_data.append({
            "reserva": {
                "id": reserva.id,
                "fecha_creacion": reserva.fecha_creacion,
                "fecha": reserva.fecha,
                "hora_inicio": reserva.hora_inicio,
                "estado": reserva.estado,
                "personas": reserva.personas,
            },
            "mesa": {
                "numero": mesa.numero,
                "capacidad": mesa.capacidad,
            },
            "usuario": {
                "id": reserva.usuario_id,
                "nombre": user.name,
                "cedula": user.cedula,
            },
        })

    return APIResponse(
        code=200,
        status="success",
        message="Reservations retrieved successfully",
        data={"reservas": reservas_data},
    )


@router.put("/cancel/{reserva_id}/")
def cancel_reserva(reserva_id: int, session: SessionDep) -> APIResponse:
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Cambiar el estado de la reserva a "cancelada"
    reserva.estado = "cancelada"

    # Actualizar la reserva en la base de datos
    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return APIResponse(
        code=200,
        status="success",
        message="Reservation cancelled successfully",
        data={
            "reserva": reserva
        },
    )


@router.delete("/{reserva_id}/")
def delete_reserva(reserva_id: int, session: SessionDep) -> APIResponse:
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Eliminar la reserva
    session.delete(reserva)
    session.commit()

    return APIResponse(
        code=200,
        status="success",
        message="Reservation deleted successfully",
        data={},
    )


@router.put("/{reserva_id}")
def update_reserva(reserva_id: int, reserva: ReservaUpdate, session: SessionDep) -> APIResponse:
    reserva_db = session.get(Reserva, reserva_id)
    if not reserva_db:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Actualizar la reserva
    reserva_db.fecha_creacion = datetime.now()
    reserva_db.fecha = reserva.fecha
    reserva_db.hora_inicio = reserva.hora
    reserva_db.personas = reserva.personas

    # Actualizar el estado de la reserva
    reserva_db.estado = reserva.estado

    # Obtener la nueva mesa con la capacidad requerida
    mesa_nueva = select_table(
        reserva.personas, reserva.fecha, reserva.hora, session, reserva_db.mesa_id)
    if not mesa_nueva:
        raise HTTPException(status_code=404, detail="No available table found")

    # Actualizar la mesa de la reserva
    reserva_db.mesa_id = mesa_nueva.id

    # Obtener nombre y cedula del usuario
    user = session.exec(select(User.id, User.name).where(
        User.cedula == reserva.cedula)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reserva_db.usuario_id = user.id

    # Actualizar la reserva en la base de datos
    session.add(reserva_db)
    session.commit()
    session.refresh(reserva_db)

    return APIResponse(
        code=200,
        status="success",
        message="Reservation updated successfully",
        data={
            "reserva": reserva_db
        },
    )
