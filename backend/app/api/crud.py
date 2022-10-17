from typing import List
from sqlalchemy.orm import Session
from app.api import models, schemas
from uuid import UUID
from fastapi import HTTPException, status


def get_or_create_orgs(db: Session, orgs: List[schemas.Org]):
    new_orgs = []

    for org in orgs:
        existing_author = (
            db.query(models.Org).filter(models.Org.name == org.name).first()
        )

        if existing_author is None:
            new_orgs.append(models.Org(id=org.id, name=org.name))
        else:
            new_orgs.append(existing_author)

    return new_orgs


def get_or_create_authors(db: Session, authors: List[schemas.Author]):
    new_authors = []

    for author in authors:
        existing_author = (
            db.query(models.Author).filter(models.Author.id == author.id).first()
        )

        if existing_author is None:
            new_author = models.Author(
                id=author.id, name=author.name, orgs=get_or_create_orgs(db, author.orgs)
            )

            new_authors.append(new_author)
        else:
            new_authors.append(existing_author)

    return new_authors


def get_or_create_keywords(db: Session, keywords: List[schemas.Keyword]):
    new_keywords = []

    for keyword in keywords:
        existing_keyword = (
            db.query(models.Keyword).filter(models.Keyword.name == keyword.name).first()
        )

        if existing_keyword is None:
            new_keywords.append(models.Keyword(id=keyword.id, name=keyword.name))
        else:
            new_keywords.append(existing_keyword)

    return new_keywords


def get_or_create_fos(db: Session, fos_list: List[schemas.Fos]):
    new_fos = []

    for fos in fos_list:
        existing_fos = db.query(models.Fos).filter(models.Fos.name == fos.name).first()

        if existing_fos is None:
            new_fos.append(models.Fos(id=fos.id, name=fos.name))
        else:
            new_fos.append(existing_fos)

    return new_fos


def get_text(db: Session, text_id: UUID):
    text = db.query(models.Text).filter(models.Text.id == text_id).first()

    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Text not found"
        )

    return text


def get_texts(db: Session, skip: int, limit: int):
    return db.query(models.Text).offset(skip).limit(limit).all()


def create_text(db: Session, text: schemas.TextBase):

    new_text = models.Text(
        title=text.title,
        year=text.year,
        abstract=text.abstract,
        venue_name=text.venue_name,
        keywords=get_or_create_keywords(db, text.keywords),
        authors=get_or_create_authors(db, text.authors),
        fos=get_or_create_fos(db, text.fos),
    )

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    return new_text


def delete_text(db: Session, text_id: UUID):
    text = get_text(db, text_id)

    db.delete(text)
    db.commit()

    return text


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Author).offset(skip).limit(limit).all()


def get_author(db: Session, author_id: UUID):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )

    return author


def create_author(db: Session, author: schemas.AuthorBase):
    new_author = models.Author(
        name=author.name, orgs=get_or_create_orgs(db, author.orgs)
    )

    db.add(new_author)
    db.commit()
    db.refresh(new_author)

    return new_author


def update_author(db: Session, author_id: UUID, author: schemas.AuthorBase):
    author_to_update = get_author(db, author_id)

    author_to_update.name = author.name
    author_to_update.orgs = get_or_create_orgs(db, author.orgs)

    db.commit()

    return author


def delete_author(db: Session, author_id: UUID):
    author = get_author(db, author_id)

    db.delete(author)
    db.commit()

    return author


def create_citation(db: Session, citation: schemas.Citation):
    if citation.text_id_from == citation.text_id_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Text cannot cite yourself"
        )

    existing_citation = (
        db.query(models.Citation)
        .filter(
            models.Citation.text_id_from == citation.text_id_from,
            models.Citation.text_id_to == citation.text_id_to,
        )
        .first()
    )

    if existing_citation is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This citation is already exists",
        )

    new_citation = models.Citation(
        text_id_from=citation.text_id_from, text_id_to=citation.text_id_to
    )
    db.add(new_citation)

    cited_text = (
        db.query(models.Text).filter(models.Text.id == citation.text_id_to).first()
    )
    quoting_text = (
        db.query(models.Text).filter(models.Text.id == citation.text_id_from).first()
    )

    if cited_text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quoted text does not exist"
        )
    if quoting_text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quoting text does not exist",
        )

    cited_text.n_citation = cited_text.n_citation + 1

    db.commit()

    return new_citation
