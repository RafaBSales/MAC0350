from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory=["templates", "templates/partials"])

curtidas = 0

@app.get("/home",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/home/pagina1"})

@app.get("/home/curtidas",response_class=HTMLResponse)
async def get_curtidas(request: Request):
    global curtidas
    return f"Curtidas: {curtidas}"

@app.post("/home/curtidas",response_class=HTMLResponse)
async def curtir(request: Request):
    global curtidas
    curtidas += 1
    return f"Curtidas: {curtidas}"

@app.delete("/home/curtidas",response_class=HTMLResponse)
async def deletar_curtidas(request: Request):
    global curtidas
    curtidas = 0
    return f"Curtidas: {curtidas}"

@app.get("/home/pagina1", response_class=HTMLResponse)
async def pag1(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/home/pagina1"})
    return templates.TemplateResponse(request, "pagina_1.html")

@app.get("/home/pagina2", response_class=HTMLResponse)
async def pag2(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html", {"pagina": "/home/pagina2"})
    return templates.TemplateResponse(request, "pagina_2.html")
