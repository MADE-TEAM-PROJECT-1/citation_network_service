from typing import List
from uuid import UUID

from app.api import crud, models, schemas
from app.api.database import SessionLocal, engine
from app.core.config import SCHEMA_NAME
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.schema import CreateSchema


class SessionManager:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, _, _a, _b):
        self.db.close()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    if not engine.dialect.has_schema(engine, SCHEMA_NAME):
        engine.execute(CreateSchema(SCHEMA_NAME))
    models.Base.metadata.create_all(bind=engine)


@app.get(
    "/users/registration/",
    status_code=status.HTTP_200_OK,
    response_class=RedirectResponse,
)
def register_user(request: Request, login: str, password: str, email: str):
    with SessionManager() as db:
        try:
            crud.try_add_user(db, login, password, email)
        except HTTPException as ex:
            get_params = (
                "?error=" + "+".join(ex.detail.split(" ")) + "&error_form=registration"
            )
            return RedirectResponse(f"/login/{get_params}")
        return RedirectResponse("/texts/")


@app.get("/login/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def login_page(request: Request, error: str = "", error_form: str = ""):
    return templates.TemplateResponse(
        "signin.html", {"request": request, "error": error, "error_form": error_form}
    )


@app.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get(
    "/users/get_user/", response_model=schemas.User, status_code=status.HTTP_200_OK
)
def get_user(login: str):
    with SessionManager() as db:
        return schemas.User.from_orm(crud.get_user_by_login(db, login))


@app.get(
    "/users/login_user/",
    status_code=status.HTTP_200_OK,
    response_class=RedirectResponse,
)
def login_user(login: str, password: str):
    with SessionManager() as db:
        try:
            crud.try_login(db, login, password)
        except HTTPException as ex:
            get_params = (
                "?error=" + "+".join(ex.detail.split(" ")) + "&error_form=login"
            )
            return RedirectResponse(f"/login/{get_params}")
        return RedirectResponse("/texts/")


@app.put(
    "/users/change_password",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
)
def change_password(User_id: UUID, new_password: str):
    with SessionManager() as db:
        return schemas.User.from_orm(crud.change_password(db, User_id, new_password))


@app.get("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def get_author(author_id: UUID):
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.get_author(db, author_id))


@app.get(
    "/authors/", response_model=List[schemas.Author], status_code=status.HTTP_200_OK
)
def get_authors(skip: int = 0, limit: int = 10):
    with SessionManager() as db:
        return [
            schemas.Author.from_orm(author)
            for author in crud.get_authors(db, skip, limit)
        ]


@app.delete("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def delete_author(author_id: UUID):
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.delete_author(db, author_id))


@app.put("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def update_author(author_id: UUID, author: schemas.AuthorBase):
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.update_author(db, author_id, author))


@app.post(
    "/author/", response_model=schemas.Author, status_code=status.HTTP_201_CREATED
)
def create_author(author: schemas.AuthorBase):
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.create_author(db, author))


@app.get(
    "/text/",
    response_model=schemas.Text,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def get_text(request: Request, text_id: UUID):
    with SessionManager() as db:
        text = crud.get_text(db, text_id)
        return templates.TemplateResponse(
            "text.html",
            {"request": request, "text": text},
        )


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.get("/texts/", response_model=List[schemas.Text], status_code=status.HTTP_200_OK)
def get_texts(request: Request, skip: int = 0, limit: int = 10):
    with SessionManager() as db:
        texts = crud.get_texts(db, skip, limit)

        return templates.TemplateResponse(
            "list-articles.html", {"request": request, "texts": texts}
        )


# @app.post("/text/", response_model=schemas.Text, status_code=status.HTTP_201_CREATED)
# def create_text(text: schemas.TextBase):
#     with SessionManager() as db:
#         return schemas.Text.from_orm(crud.create_text(db, text))


@app.delete("/text/", response_model=schemas.Text, status_code=status.HTTP_200_OK)
def delete_text(text_id: UUID):
    with SessionManager() as db:
        return schemas.Text.from_orm(crud.delete_text(db, text_id))


@app.post(
    "/citation/", response_model=schemas.Citation, status_code=status.HTTP_201_CREATED
)
def create_citation(citation: schemas.Citation):
    with SessionManager() as db:
        return schemas.Citation.from_orm(crud.create_citation(db, citation))


@app.get(
    "/search/", response_model=List[schemas.TextSearchResults], status_code=status.HTTP_200_OK, 
)
def search_request(request: Request, tag: str = "", author: str = "", venue_name: str = "", year:str = ""):
    with SessionManager() as db:
        texts = [
            schemas.TextSearchResults.from_orm(request)
            for request in crud.get_search(db, tag, author, venue_name, year)
        ]
        if texts !=[]:
            return templates.TemplateResponse(
                "list-articles.html", {"request" : request, "texts": texts}
            )
        else:
            return RedirectResponse('/texts/')


@app.get("/text/add", status_code=status.HTTP_200_OK)
def add_text_page(request: Request):
    return templates.TemplateResponse()


@app.post("/text/add", status_code=status.HTTP_200_OK)
def add_text(text: schemas.TextInput):
    with SessionManager() as db:
        text_id = str(crud.add_text(db, text))
        return RedirectResponse(
            f"/text/?text_id={text_id}", status_code=status.HTTP_303_SEE_OTHER
        )
