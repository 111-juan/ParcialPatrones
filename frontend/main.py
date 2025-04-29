from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Servir archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/", response_class=HTMLResponse)
def read_login():
    with open("html/login.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.get("/register/", response_class=HTMLResponse)
def read_register():
    with open("html/registro.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.get("/reservas/create/", response_class=HTMLResponse)
def read_reservas():
    with open("html/reservas.html", "r") as file:
        return HTMLResponse(content=file.read())


@app.get("/reservas/view/", response_class=HTMLResponse)
def view_reservas():
    with open("html/admin-panel.html", "r") as file:
        return HTMLResponse(content=file.read())
