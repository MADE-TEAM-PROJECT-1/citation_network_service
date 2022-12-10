from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import date, datetime, time
from uuid import UUID, uuid1

class Keyword(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    name: str

    class Config:
        orm_mode = True

class Fos(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    name: str

    class Config:
        orm_mode = True


class Org(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    name: str

    class Config:
        orm_mode = True

class Tag(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    name: str

    class Config:
        orm_mode = True

class AuthorBase(BaseModel):
    name: str
    orgs: List[Org]


class Author(AuthorBase):
    id: Optional[UUID] = Field(default_factory=uuid1)

    class Config:
        orm_mode = True


class TextInput(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    n_citation: int
    title: str
    year: int
    abstract: str
    venue_name: str
    keywords: List[Keyword]
    authors: List[Author]
    fos: List[Fos]

    class Config:
        orm_mode = True

class TextBase(BaseModel):
    title: str
    year: int
    abstract: str
    venue_name: str
    keywords: List[Keyword] 
    authors: List[Author]
    fos: List[Fos]

class Text(TextBase):
    id: Optional[UUID] = Field(default_factory=uuid1)
    n_citation: int

    class Config:
        orm_mode = True


class Citation(BaseModel):
    text_id_from: UUID
    text_id_to: UUID

    class Config:
        orm_mode = True

class User(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    login: str
    password_hash: str
    email: str
    author_id = UUID 

    class Config:
        orm_mode = True


class UserRegistration(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    author_id: Optional[UUID] = Field(default_factory=uuid1)
    login: str
    email: str
    password: str

class SearchResults(BaseModel):
    title: str
    year: int
    abstract: str
    venue_name: str
    keywords: List[Keyword]
    authors: List[Author]
    tags: List[Tag]
    fos: List[Fos]

    class Config:
        orm_mode = True

class SearchHistory(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    user_id: Optional[UUID] = Field(default_factory=uuid1, nullable=True)
    request_date: date
    search_tag: str 
    author: str
    venue_name: str 
    year: int

    class Config: 
        orm_mode = True

class ArticlesOpened(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    user_id: Optional[UUID] = Field(default_factory=uuid1)
    text_id: Optional[UUID] = Field(default_factory=uuid1)
    request_date: date

    class Config: 
        orm_mode = True

class ArticlesRated(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid1)
    user_id: Optional[UUID] = Field(default_factory=uuid1)
    text_id: Optional[UUID] = Field(default_factory=uuid1)
    request_date: date
    mark : Literal[0, 1, 2, 3, 4, 5]

    class Config:
        orm_nodel = True




