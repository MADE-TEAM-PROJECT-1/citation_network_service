
from typing import List

from fastapi import FastAPI, Depends, status
from sqlalchemy.schema import CreateSchema

from uuid import UUID
from app.api import crud, models, schemas
from app.api.database import SessionLocal, engine
from app.core.config import SCHEMA_NAME


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


class SessionManager:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, _, _a, _b):
        self.db.close()


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    if not engine.dialect.has_schema(engine, SCHEMA_NAME):
        engine.execute(CreateSchema(SCHEMA_NAME))
    models.Base.metadata.create_all(bind=engine)


@app.post("/users/registration/", status_code=status.HTTP_200_OK)
def register_user(user: schemas.User):
    with SessionManager() as db:
        return schemas.User.from_orm(crud.try_add_user(db, user))


@app.get("/users/get_user/",response_model = schemas.User, status_code=status.HTTP_200_OK)
def get_user(login: str):
    with SessionManager() as db:
        return schemas.User.from_orm(crud.get_user_by_login(db, login))

@app.post("/users/login_user/", status_code=status.HTTP_200_OK)
def login_user(login :str, password :str):
    with SessionManager() as db:
        return schemas.User.from_orm(crud.try_login(db, login, password))

@app.put("/users/change_password", response_model=schemas.User, status_code=status.HTTP_200_OK)
def change_password( User_id: UUID, new_password: str):
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
        return [schemas.Author.from_orm(author) for author in crud.get_authors(db, skip, limit)]


@app.delete("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def delete_author(author_id: UUID):
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.delete_author(db, author_id))


@app.put("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def update_author(
    author_id: UUID, author: schemas.AuthorBase
):
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.update_author(db, author_id, author))


@app.post(
    "/author/", response_model=schemas.Author, status_code=status.HTTP_201_CREATED
)
def create_author(author: schemas.AuthorBase):
    with SessionManager() as db:
        return schemas.Author.from_orm(crud.create_author(db, author))


@app.get("/text/", response_model=schemas.Text, status_code=status.HTTP_200_OK)
def get_text(text_id: UUID):
    with SessionManager() as db:
        return schemas.Text.from_orm(crud.get_text(db, text_id))


@app.get("/texts/", response_model=List[schemas.Text], status_code=status.HTTP_200_OK)
def get_texts(skip: int = 0, limit: int = 10):
    with SessionManager() as db:
        return [schemas.Text.from_orm(text) for text in crud.get_texts(db, skip, limit)]


@app.post("/text/", response_model=schemas.Text, status_code=status.HTTP_201_CREATED)
def create_text(text: schemas.TextBase):
    with SessionManager() as db:
        return schemas.Text.from_orm(crud.create_text(db, text))


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
