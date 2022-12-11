import logging
import sys
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid1
import pandas as pd

from app.api.graph_visualization import graph_model
from app.api import crud, models, schemas
from app.api.database import SessionLocal, engine
from app.core.config import SCHEMA_NAME, LOGS_DIR, LOGS_MESSAGE_FORMAT
from fastapi import FastAPI, HTTPException, Request, status, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.schema import CreateSchema
from pydantic import BaseModel, Field

logging.basicConfig(
    filename=LOGS_DIR, level=logging.DEBUG, format=LOGS_MESSAGE_FORMAT, filemode="a+"
)


class SessionManager:
    def __init__(self):
        logging.debug("Session starting...")
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, _, _a, _b):
        logging.debug("Session ending...")
        self.db.close()


current_user_id = None
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    if not engine.dialect.has_schema(engine, SCHEMA_NAME):
        engine.execute(CreateSchema(SCHEMA_NAME))
    models.Base.metadata.create_all(bind=engine)
    logging.info(f" table names are {engine.table_names()}")


@app.post(
    "/visualization",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
def visuaize_graph(
    request: Request,
    data: List[schemas.TextInput],
    cut_size: int = 10,
    start_id: str = "",
):
    logging.info(f"{__name__} called")
    df = crud.make_dict(data)
    logging.info(f"dataframe is {df}")
    g = graph_model(df, cut_size)
    g.build_graph(start_id)
    page = g.show_graph()
    logging.info(f"page is {page}")
    return page


@app.get(
    "/users/registration/",
    status_code=status.HTTP_200_OK,
    response_class=RedirectResponse,
)
def register_user(request: Request, login: str, password: str, email: str):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        try:
            new_user = crud.try_add_user(db, login, password, email)
        except HTTPException as ex:
            get_params = (
                "?error=" + "+".join(ex.detail.split(" ")) + "&error_form=registration"
            )
            logging.info("registered user tried to register:" + get_params)
            return RedirectResponse(f"/login/{get_params}")
        global current_user_id
        current_user_id = new_user.id
        logging.info(f"new user with id {new_user.id} is created")
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
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.User.from_orm(crud.get_user_by_login(db, login))


@app.get(
    "/users/login_user/",
    status_code=status.HTTP_200_OK,
    response_class=RedirectResponse,
)
def login_user(request: Request, login: str, password: str):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        try:
            user = crud.try_login(db, login, password)
        except HTTPException as ex:
            get_params = (
                "?error=" + "+".join(ex.detail.split(" ")) + "&error_form=login"
            )
            logging.info("failed to log in user params:" + get_params)
            return RedirectResponse(f"/login/{get_params}")
        logging.info(f"user id is {user.id}")
        # request.state.__setattr__('user', user.id)
        global current_user_id
        current_user_id = user.id
        #    logging.info(f"request user id is{request.state.user}")
        return RedirectResponse("/texts/")


@app.put(
    "/users/change_password",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
)
def change_password(request: Request, User_id: UUID, new_password: str):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.User.from_orm(crud.change_password(db, User_id, new_password))


@app.get("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def get_author(author_id: UUID):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.get_author(db, author_id))


@app.get(
    "/authors/", response_model=List[schemas.Author], status_code=status.HTTP_200_OK
)
def get_authors(skip: int = 0, limit: int = 10):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return [
            schemas.Author.from_orm(author)
            for author in crud.get_authors(db, skip, limit)
        ]


@app.delete("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def delete_author(author_id: UUID):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.delete_author(db, author_id))


@app.put("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def update_author(author_id: UUID, author: schemas.AuthorBase):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.update_author(db, author_id, author))


@app.post(
    "/author/", response_model=schemas.Author, status_code=status.HTTP_201_CREATED
)
def create_author(author: schemas.AuthorBase):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.create_author(db, author))


@app.get(
    "/text/",
    response_model=schemas.Text,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def get_text(request: Request, text_id: UUID):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        text = crud.get_text(db, text_id)
        return templates.TemplateResponse(
            "text.html",
            {"request": request, "text": text},
        )


@app.get(
    "/loggs/",
    response_model=schemas.Text,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def get_text(request: Request, search_id: UUID):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        search = crud.get_search(db, search_id)
        return templates.TemplateResponse(
            "search.html",
            {"request": request, "search": search},
        )


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    logging.info(f"{__name__} called")
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.get("/texts/", response_model=List[schemas.Text], status_code=status.HTTP_200_OK)
def get_texts(request: Request, skip: int = 0, limit: int = 10):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        texts = crud.get_texts(db, skip, limit)

        return templates.TemplateResponse(
            "list-articles.html", {"request": request, "texts": texts}
        )


@app.get(
    "/loggs/search",
    response_model=List[schemas.SearchHistory],
    status_code=status.HTTP_200_OK,
)
def get_stored_search(request: Request, user_id: UUID, limit: int = 10):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        searches = [
            schemas.SearchHistory.from_orm(request)
            for request in crud.get_search_loggs(db, user_id, limit)
        ]
        logging.info(f"searches are {searches}")
        return templates.TemplateResponse(
            "list-searches.html", {"request": request, "searches": searches}
        )


@app.delete("/text/", response_model=schemas.Text, status_code=status.HTTP_200_OK)
def delete_text(text_id: UUID):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.Text.from_orm(crud.delete_text(db, text_id))


@app.post(
    "/citation/", response_model=schemas.Citation, status_code=status.HTTP_201_CREATED
)
def create_citation(citation: schemas.Citation):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        return schemas.Citation.from_orm(crud.create_citation(db, citation))


@app.get(
    "/search/",
    response_model=List[schemas.SearchResults],
    status_code=status.HTTP_200_OK,
)
def search_request(
    request: Request,
    tag: str = "",
    author: str = "",
    venue_name: str = "",
    year: str = "",
):
    logging.info(f"{__name__} called")
    with SessionManager() as db:
        global current_user_id
        logging.info(f"current_user_id is {current_user_id}")
        crud.create_stored_search(db, current_user_id, tag, author, venue_name, year)
        texts = [
            schemas.SearchResults.from_orm(request)
            for request in crud.get_search(db, tag, author, venue_name, year)
        ]
        if texts != []:
            return templates.TemplateResponse(
                "list-articles.html", {"request": request, "texts": texts}
            )
        else:
            return RedirectResponse("/texts/")


@app.post("/text/", response_model=schemas.Text, status_code=status.HTTP_201_CREATED)
def create_text(text: schemas.TextBase):
    with SessionManager() as db:
        return schemas.Text.from_orm(crud.create_text(db, text))


@app.get("/text/add", status_code=status.HTTP_200_OK)
def add_text_page(request: Request):
    logging.info(f"{__name__} called")
    return templates.TemplateResponse("add_text.html", {"request": request})


# @app.post("/text/add_raw", status_code=status.HTTP_200_OK)
# def add_text(
#     title: str = Form(),
#     year: int = Form(),
#     abstract: str = Form(),
#     venue: str = Form(),
#     keywords: str = Form(),
#     fos: str = Form,
# ):

#     logging.info(f"{__name__} called")

#     with SessionManager() as db:
#         author_id = (
#             db.query(models.User)
#             .filter(models.User.id == current_user_id)
#             .with_entities(models.User.author_id)
#             .first()
#             .author_id
#         )
#         author = get_author(
#             db.query(models.Author).filter(models.Author.id == author_id)
#         )
#         text = schemas.TextBase(
#             title=title,
#             year=year,
#             abstract=abstract,
#             venue_name=venue,
#             keywords=keywords.split(", "),
#             fos=fos.split(", "),
#             authors=[author],
#         )
#         new_text_id = str(crud.create_text(db, text).id)
#         return RedirectResponse(
#             f"/text/?text_id={new_text_id}", status_code=status.HTTP_303_SEE_OTHER
#         )


@app.post("/recomendations/articles", status_code=status.HTTP_200_OK)
def get_article_recomendation(text_id: UUID):
    with SessionManager() as db:
        return crud.get_article_recomendation(db, current_user_id)
