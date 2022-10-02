from sqlalchemy.orm import Session
import models, schemas
from uuid import UUID
from fastapi import HTTPException, status


def get_text(db: Session, text_id: UUID):
    text = db.query(models.Text).filter(models.Text.id == text_id).first()

    if text in None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    return text


def get_texts_by_author(db: Session, author_id: int):
    return db.query(models.Text).filter(author_id.in_(models.Text.authors)).all()


def create_text(db: Session, text: schemas.Text):
    new_text = models.Text(
        title=text.title,
        year=text.year,
        n_citation=text.n_citation,
        abstract=text.abstract,
        venue_name=text.venue_name,
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


def update_text(db: Session, text_id: UUID, text: schemas.Text):
    text_to_update = get_text(db, text_id)

    text_to_update.title = text.title
    text_to_update.year = text.year
    text_to_update.n_citations = text.n_citations
    text_to_update.abstract = text.abstract
    text_to_update.venue_name = text.venue_name

    db.commit()
    db.refresh(text_to_update)

    return text_to_update


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Author).offset(skip).limit(limit).all()


def get_author(db: Session, author_id: UUID):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )

    return author


def create_author(db: Session, author: schemas.Author):
    new_author = models.Author(name=author.name)

    db.add(new_author)
    db.commit()
    db.refresh(new_author)

    return new_author


def update_author(db: Session, author_id: UUID, author: schemas.Author):
    author_to_update = get_author(db, author_id)

    author_to_update.name = author.name

    db.commit()
    db.refresh(author_to_update)

    return author


def delete_author(db: Session, author_id: UUID):
    author = get_author(db, author_id)

    db.delete(author)
    db.commit()

    return author
