from fastapi import FastAPI, Request, HTTPException, Response, Depends, Cookie, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class User(BaseModel):
    nome: str
    senha: str
    bio: str

users_db = []

@app.get("/")
def get_page(request: Request):
    return templates.TemplateResponse(
                request=request,
                name="index.html"
            )

@app.post("/users")
def criar_usuario(user: User):
    users_db.append(user.model_dump())
    return {"user": user.nome}

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
                request=request,
                name="login.html"
            )

@app.post("/login")
def login(request: dict, response: Response):
    usuario_encontrado = None
    for u in users_db:
        if u["nome"] == request["nome"]:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario_encontrado["senha"] != request["senha"]:
        raise HTTPException(status_code=401, detail="Senha errada.")
    
    # O servidor diz ao navegador: "Guarde esse nome no cookie 'session_user'"
    response.set_cookie(key="session_user", value=request["nome"])
    return {"message": "Logado com sucesso"}

def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    # O FastAPI busca automaticamente um cookie chamado 'session_user'
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    
    user = next((u for u in users_db if u["nome"] == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

# 3. Rota Protegida
@app.get("/home")
def show_profile(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={"user": user["nome"], "bio": user["bio"]}
    )

