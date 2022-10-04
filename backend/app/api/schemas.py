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


class AuthorBase(BaseModel):
    name: str
    orgs: List[Org]


class Author(AuthorBase):
    id: Optional[UUID] = Field(default_factory=uuid1)

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

    # class Config:
    #     orm_mode = True

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
