from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional


app = FastAPI()

# Servir archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/", response_class=HTMLResponse)
def read_login():
    with open("html/login.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.get("/register/", response_class=HTMLResponse)
def read_register(adminCreate: Optional[bool] = None):
    with open("html/registro.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.get("/menu/", response_class=HTMLResponse)
def read_menu():
    with open("html/menu.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.get("/user/reservas/", response_class=HTMLResponse)
def read_reservas():
    with open("html/reservas-cliente.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.get("/reservas/create/{userId}", response_class=HTMLResponse)
def create_reservas(userId: int):
    with open("html/reservas.html", "r") as file:
        content = file.read().replace("{{userId}}", str(userId))
        return HTMLResponse(content=content)


@app.get("/reservas/view/", response_class=HTMLResponse)
def view_reservas():
    with open("html/admin-panel.html", "r") as file:
        return HTMLResponse(content=file.read())
