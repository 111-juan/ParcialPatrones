from typing import Annotated
from sqlmodel import select
from fastapi import APIRouter, Depends, HTTPException, Query


from models.user import User, UserAuth, UserCreate, UserLogin
from dependencies.database import SessionDep
from dependencies.security import hash_password
from models.api_response import APIResponse
from dependencies.security import generate_secure_password

router = APIRouter(prefix="/users")


@router.post("/register/")
def create_user(user: UserCreate, session: SessionDep) -> APIResponse:
    # Verificar si el correo ya está registrado
    existing_user = session.exec(
        select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Email already registered")

    try:
        # Crear el usuario principal
        userInfo = User(**user.model_dump(), roles=["user"])
        session.add(userInfo)
        session.commit()
        session.refresh(userInfo)

        # Crear la autenticación del usuario
        userAuth = UserAuth(
            email=user.email, password=hash_password(user.password), user_id=userInfo.id
        )
        session.add(userAuth)
        session.commit()
        session.refresh(userAuth)

        # Respuesta exitosa
        return APIResponse(
            code=201,
            status="success",
            message="User created successfully",
            data={
                "user": {
                    "id": userInfo.id,
                    "email": userInfo.email,
                    "name": userInfo.name,
                    "roles": userInfo.roles,
                }
            },
        )
    except Exception as e:
        # Manejar errores inesperados
        session.rollback()  # Revertir cambios en caso de error
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred: " + str(e)
        )


def login_user(user: UserLogin, session: SessionDep) -> APIResponse:
    try:
        # Verificar si el usuario existe en la tabla UserAuth
        user_auth = session.exec(
            select(UserAuth).where(UserAuth.email == user.email)
        ).first()
        if not user_auth:
            raise HTTPException(status_code=404, detail="User not found")

        # Verificar si la contraseña es correcta
        if user_auth.password != hash_password(user.password):
            raise HTTPException(status_code=401, detail="Incorrect password")

        # Obtener información del usuario desde la tabla User
        user_info = session.exec(
            select(User.id, User.name, User.roles).where(
                User.id == user_auth.user_id)
        ).first()
        if not user_info:
            raise HTTPException(
                status_code=404, detail="User information not found")

        # Respuesta exitosa
        return APIResponse(
            code="200",
            status="success",
            message="User logged in successfully",
            data={
                "user": {
                    "id": user_info.id,
                    "name": user_info.name,
                    "roles": user_info.roles,
                }
            },
        )
    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP específicas
        raise http_exc
    except Exception as e:
        # Manejar errores inesperados
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/login")
async def login_user(user: User = Depends(login_user)):
    return user


@router.get("/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> APIResponse:
    try:
        # Obtener usuarios con paginación
        users = session.exec(
            select(User).order_by(User.name).offset(offset).limit(limit)
        ).all()

        # Verificar si no hay usuarios
        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        # Respuesta exitosa
        return APIResponse(
            code=200,
            status="success",
            message="Users retrieved successfully",
            data={"users": users},
        )
    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP específicas
        raise http_exc
    except Exception as e:
        # Manejar errores inesperados
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{user_id}")
def read_user(user_id: int, session: SessionDep) -> APIResponse:
    try:
        # Buscar el usuario por ID
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Respuesta exitosa
        return APIResponse(
            code=200,
            status="success",
            message="User retrieved successfully",
            data={"user": user.model_dump()},
        )
    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP específicas
        raise http_exc
    except Exception as e:
        # Manejar errores inesperados
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/cedula/{cedula}")
def read_user_by_cedula(cedula: str, session: SessionDep) -> APIResponse:
    try:
        # Buscar el usuario por cédula
        id = session.exec(
            select(User.id).where(User.cedula == cedula)
        ).first()
        if not id:
            raise HTTPException(status_code=404, detail="User not found")

        # Respuesta exitosa
        return APIResponse(
            code=200,
            status="success",
            message="User retrieved successfully",
            data={"id": id},
        )
    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP específicas
        raise http_exc
    except Exception as e:
        # Manejar errores inesperados
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete("/{user_id}")
def delete_user(user_id: int, session: SessionDep) -> APIResponse:
    try:
        # Buscar el usuario por ID
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Eliminar el usuario
        session.delete(user)
        session.commit()

        # Respuesta exitosa
        return APIResponse(
            code=200,
            status="success",
            message="User deleted successfully",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                }
            },
        )
    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP específicas
        raise http_exc
    except Exception as e:
        # Manejar errores inesperados
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.put("/{user_id}")
def update_user(user_id: int, user: UserCreate, session: SessionDep) -> APIResponse:
    try:
        # Buscar el usuario por ID
        user_db = session.get(User, user_id)
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        # Actualizar los campos del usuario
        user_db.name = user.name
        user_db.email = user.email

        # Guardar los cambios en la base de datos
        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        # Respuesta exitosa
        return APIResponse(
            code=200,
            status="success",
            message="User updated successfully",
            data={
                "user": {
                    "id": user_db.id,
                    "email": user_db.email,
                    "name": user_db.name,
                    "roles": user_db.roles,
                }
            },
        )
    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP específicas
        raise http_exc
    except Exception as e:
        # Manejar errores inesperados
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.put("/{user_id}/roles/")
def update_user_roles(user_id: int, roles: list[str], session: SessionDep) -> APIResponse:
    try:
        # Buscar el usuario por ID
        user_db = session.get(User, user_id)
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")

        # Actualizar los roles del usuario
        user_db.roles = roles

        # Guardar los cambios en la base de datos
        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        # Respuesta exitosa
        return APIResponse(
            code=200,
            status="success",
            message="User roles updated successfully",
            data={
                "user": {
                    "id": user_db.id,
                    "email": user_db.email,
                    "name": user_db.name,
                    "roles": user_db.roles,
                }
            },
        )
    except HTTPException as http_exc:
        # Re-lanzar excepciones HTTP específicas
        raise http_exc
    except Exception as e:
        # Manejar errores inesperados
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/random-password/")
def generate_random_password() -> APIResponse:
    return APIResponse(
        code=200,
        status="success",
        message="Password generated successfully",
        data={
            "password": generate_secure_password()
        },
    )
