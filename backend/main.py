from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from dependencies.database import create_db_and_tables
from routers import users
from routers import reserva
from models.api_response import APIResponse


app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            code=exc.status_code,
            status="error",
            message=exc.detail,
        ).model_dump()
    )


# Permitir CORS (ajusta origins según sea necesario)
app.add_middleware(
    CORSMiddleware,
    # Cambia "*" por la URL de tu frontend en producción
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (POST, GET, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# agregar routers
app.include_router(users.router)
app.include_router(reserva.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
