from typing import List

from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema
from app.core import config
from uuid import UUID
from app.api import crud, models, schemas
from app.api.database import SessionLocal, engine


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

if not engine.dialect.has_schema(engine, config.SCHEMA_NAME):
    engine.execute(CreateSchema(config.SCHEMA_NAME))
models.Base.metadata.create_all(bind=engine)


@app.get("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def get_author(author_id: UUID, db: Session = Depends(get_db)):
    return crud.get_author(db, author_id)


@app.get(
    "/authors/", response_model=List[schemas.Author], status_code=status.HTTP_200_OK
)
def get_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_authors(db, skip, limit)


@app.delete("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def delete_author(author_id: UUID, db: Session = Depends(get_db)):
    return crud.delete_author(db, author_id)


@app.put("/author/", response_model=schemas.Author, status_code=status.HTTP_200_OK)
def update_author(
    author_id: UUID, author: schemas.AuthorBase, db: Session = Depends(get_db)
):
    return crud.update_author(db, author_id, author)


@app.post(
    "/author/", response_model=schemas.Author, status_code=status.HTTP_201_CREATED
)
def create_author(author: schemas.AuthorBase, db: Session = Depends(get_db)):
    return crud.create_author(db, author)


@app.get("/text/", response_model=schemas.Text, status_code=status.HTTP_200_OK)
def get_text(text_id: UUID, db: Session = Depends(get_db)):
    return crud.get_text(db, text_id)


@app.get("/texts/", response_model=List[schemas.Text], status_code=status.HTTP_200_OK)
def get_texts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_texts(db, skip, limit)


@app.post("/text/", response_model=schemas.Text, status_code=status.HTTP_201_CREATED)
def create_text(text: schemas.TextBase, db: Session = Depends(get_db)):
    return crud.create_text(db, text)


@app.delete("/text/", response_model=schemas.Text, status_code=status.HTTP_200_OK)
def delete_text(text_id: UUID, db: Session = Depends(get_db)):
    return crud.delete_text(db, text_id)


@app.post(
    "/citation/", response_model=schemas.Citation, status_code=status.HTTP_201_CREATED
)
def create_citation(citation: schemas.Citation, db: Session = Depends(get_db)):
    return crud.create_citation(db, citation)
