from fastapi import FastAPI, Request, HTTPException, Response, Depends, Cookie, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated, Optional
from models import Receita, Tag
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy import event
from sqlalchemy.orm import selectinload

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

PAGE_SIZE=10

app = FastAPI(lifespan=initFunction)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

arquivo_sqlite = "caderno_de_receitas.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def get_index_page(request: Request):
    return templates.TemplateResponse(
                request,
                "index.html",
            )

@app.get("/busca")
def get_search_page(request: Request):
    return templates.TemplateResponse(
                request,
                "busca.html",
            )

def buscar_receitas(busca):
    with Session(engine) as session:
        query = select(Receita).options(selectinload(Receita.tags)).where(Receita.nome.contains(busca))
        return session.exec(query).all()

def busca_receita_por_id(id: int):
    with Session(engine) as session:
        query = select(Receita).options(selectinload(Receita.tags)).where(Receita.id == id)
        return session.exec(query).first()

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str=''):
    receitas = buscar_receitas(busca)
    for receita in receitas:
        if len(receita.descricao) > 120:
            receita.descricao = receita.descricao[:120] + "..."

        receita.tags = sorted(receita.tags, key=lambda tag: tag.nome)

    return templates.TemplateResponse(request, "lista_receitas.html", {"receitas": receitas})



@app.get("/receita/criar")
def get_create_page(request: Request):
    return templates.TemplateResponse(
                request,
                "criar.html"
            )

@app.post("/receita/criar")
def criar_receita(request: Request, nome: str=Form(...), tags: Optional[str]=Form(None), descricao: str=Form(...)):
    if not tags: tags = ""
    tag_names = list(set([tag.strip() for tag in tags.split(",") if tag.strip()]))
    tags_list = []
    with Session(engine) as session:
        for tag_name in tag_names:
            tag = session.exec(select(Tag).where(Tag.nome == tag_name)).first()
            if tag:
                tags_list.append(tag)
            else:
                new_tag = Tag(nome=tag_name)
                session.add(new_tag)
                tags_list.append(new_tag)

        receita = Receita(nome=nome, descricao=descricao, tags=tags_list)
        session.add(receita)
        session.commit()
        session.refresh(receita)

        response = Response()
        response.headers["HX-Redirect"] = "/busca"
        return response


@app.get("/receita")
def get_recipe_page(request: Request, id: int):
    receita: Receita | None = busca_receita_por_id(id)
    if (not receita):
        raise HTTPException(404, "Receita não encontrada")
    return templates.TemplateResponse(
                request,
                "receita.html",
                {"receita": receita}
            )

@app.get("/receita/editar")
def get_edit_recipe_page(request: Request, id: int):
    receita: Receita | None = busca_receita_por_id(id)
    if (not receita):
        raise HTTPException(404, "Receita não encontrada")
    return templates.TemplateResponse(
                request,
                "editar.html",
                {"receita": receita}
            )


@app.put("/receita/editar")
def edit_recipe(request: Request, id: int, nome: str=Form(...), tags: Optional[str]=Form(None), descricao: str=Form(...)):
    if not tags: tags = ""
    tag_names = list(set([tag.strip() for tag in tags.split(",") if tag.strip()]))
    tags_list = []

    with Session(engine) as session:
        for tag_name in tag_names:
            tag = session.exec(select(Tag).where(Tag.nome == tag_name)).first()
            if tag:
                tags_list.append(tag)
            else:
                new_tag = Tag(nome=tag_name)
                session.add(new_tag)
                tags_list.append(new_tag)

        query = select(Receita).where(Receita.id == id)
        receita = session.exec(query).first()
        if (not receita):
            raise HTTPException(404, "Receita não encontrada")
        receita.nome = nome
        receita.descricao = descricao
        receita.tags = tags_list
        session.commit()
        session.refresh(receita)

        response = Response()
        response.headers["HX-Redirect"] = f"/receita?id={id}"
        return response


@app.delete("/receita/deletar")
def delete_recipe(request: Request, id: int):
    with Session(engine) as session:
        query = select(Receita).where(Receita.id == id)
        receita = session.exec(query).first()
        if (not receita):
            raise HTTPException(404, "Receita não encontrada")
        session.delete(receita)
        session.commit()
        response = Response()
        response.headers["HX-Redirect"] = "/busca"
        return response
