from typing import Optional, List
from pydantic import BaseModel, Field
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
    tags: List[Tag]


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
