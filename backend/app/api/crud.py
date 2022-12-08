from collections import Counter
import logging
from typing import List
from uuid import UUID, uuid1

import requests
from app.api import models, schemas
from fastapi import HTTPException, status
from passlib import context
from sqlalchemy.orm import Session
from app.core.config import SCHEMA_NAME, LOGS_DIR, LOGS_MESSAGE_FORMAT

logging.basicConfig(filename=LOGS_DIR, level=logging.DEBUG, format=LOGS_MESSAGE_FORMAT, filemode="a+")

class Hasher:
    def __init__(self):
        self.pwd_context = context.CryptContext(
            schemes=["sha256_crypt"], deprecated="auto"
        )

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

#def create_stored_search(db: Session, stored_search: schemas.StoredSearch):
#    new_stored_search = models.StoredSearch(
#        id=stored_search.id,
#        user_id = stored_search.user_id,
#        request_date = stored_search.request_date,
#        request_str = stored_search.request_str
 #   )
#    db.add(new_stored_search)
 #   db.commit()
 #   db.refresh(new_stored_search)

  #  return new_stored_search


def get_user_by_login(db: Session, login: str):
    logging.info(f"{__name__} called")
    return db.query(models.User).filter(models.User.login == login).first()


def get_user_by_id(db: Session, id: UUID):
    logging.info(f"{__name__} called")
    return db.query(models.User).filter(models.User.id == id).first()


def try_add_user(db: Session, login: str, password: str, email: str):
    logging.info(f"{__name__} called")
    password_hasher = Hasher()
    user_candidate = get_user_by_login(db, login)
    if user_candidate is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this login already exist",
        )
    real_hash = password_hasher.get_password_hash(password)
    new_user = models.User(login=login, password_hash=real_hash, email=email)
    db.add(new_user)
    db.commit()
    return new_user


def try_login(db: Session, login: str, password: str):
    logging.info(f"{__name__} called")
    password_hasher = Hasher()
    user_candidate = get_user_by_login(db, login)
    if user_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user with this login",
        )
    if not password_hasher.verify_password(password, user_candidate.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ivalid password :(",
        )
    return user_candidate


def change_password(db: Session, User_id: UUID, new_password: str):
    logging.info(f"{__name__} called")
    password_hasher = Hasher()
    user = get_user_by_id(db, User_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user with this ID",
        )
    user.password_hash = password_hasher.get_password_hash(new_password)
    db.commit()
    return user


def get_or_create_orgs(db: Session, orgs: List[schemas.Org]):
    logging.info(f"{__name__} called")
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
    logging.info(f"{__name__} called")
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
    logging.info(f"{__name__} called")
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
    logging.info(f"{__name__} called")
    new_fos = []

    for fos in fos_list:
        existing_fos = db.query(models.Fos).filter(models.Fos.name == fos.name).first()

        if existing_fos is None:
            new_fos.append(models.Fos(id=fos.id, name=fos.name))
        else:
            new_fos.append(existing_fos)

    return new_fos


def get_or_create_tags(db: Session, tags_list: List[str]):
    new_tags = []

    for tag in tags_list:
        existing_tag = db.query(models.Tags).filter(models.Tags.name == tag).first()

        if existing_tag is None:
            new_tags.append(models.Tags(id=uuid1(), name=tag))
        else:
            new_tags.append(existing_tag)

    return new_tags


def get_text(db: Session, text_id: UUID):
    logging.info(f"{__name__} called")
    text = db.query(models.Text).filter(models.Text.id == text_id).first()

    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Text not found"
        )

    return text


def get_texts(db: Session, skip: int, limit: int):
    logging.info(f"{__name__} called")
    return db.query(models.Text).offset(skip).limit(limit).all()


def create_text(db: Session, text: schemas.TextInput):

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
    logging.info(f"{__name__} called")
    text = get_text(db, text_id)

    db.delete(text)
    db.commit()

    return text


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    logging.info(f"{__name__} called")
    return db.query(models.Author).offset(skip).limit(limit).all()


def get_author(db: Session, author_id: UUID):
    logging.info(f"{__name__} called")
    author = db.query(models.Author).filter(models.Author.id == author_id).first()

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )

    return author


def create_author(db: Session, author: schemas.AuthorBase):
    logging.info(f"{__name__} called")
    new_author = models.Author(
        name=author.name, orgs=get_or_create_orgs(db, author.orgs)
    )

    db.add(new_author)
    db.commit()
    db.refresh(new_author)

    return new_author


def update_author(db: Session, author_id: UUID, author: schemas.AuthorBase):
    logging.info(f"{__name__} called")
    author_to_update = get_author(db, author_id)

    author_to_update.name = author.name
    author_to_update.orgs = get_or_create_orgs(db, author.orgs)

    db.commit()

    return author


def delete_author(db: Session, author_id: UUID):
    logging.info(f"{__name__} called")
    author = get_author(db, author_id)

    db.delete(author)
    db.commit()

    return author


def create_citation(db: Session, citation: schemas.Citation):
    logging.info(f"{__name__} called")
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


def get_search(db: Session, tag: str = "", author: str = "", venue_name: str = "", year:str = ""):
    ans_list = []

    def search_filter(answers, params):
        ans = db.query(models.Text).filter(params).limit(20).all()
        for item in ans:
            answers.append(item)
        return answers

    if venue_name == "":
        venue_name = "<!?*>"
    if year == "":
        year = 0
    else:
        try:
            year = int(year)
        except:
            return set()

    search_filter(ans_list, models.Text.tags.any(name=tag))
    search_filter(ans_list, models.Text.authors.any(name=author))
    search_filter(ans_list, models.Text.venue_name.contains(venue_name))
    search_filter(ans_list, models.Text.year==year)

    result = set(sorted(ans_list, key=Counter(ans_list).get, reverse=True))
    return result


def add_text(db: Session, text: schemas.TextInput):
    tags = requests.post(
        url="http://classification_inference:8088/predict_tags/",
        json={"title": text.title, "abstract": text.abstract},
    ).json()["predictions"]

    new_text = models.Text(
        title=text.title,
        year=text.year,
        abstract=text.abstract,
        venue_name=text.venue_name,
        keywords=get_or_create_keywords(db, text.keywords),
        authors=get_or_create_authors(db, text.authors),
        fos=get_or_create_fos(db, text.fos),
        tags=get_or_create_tags(db, tags),
    )

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    return new_text.id
