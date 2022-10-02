from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID


class Keyword(BaseModel):
    id: Optional[UUID]
    name: str

    class Config:
        orm_mode = True


class Author(BaseModel):
    id: Optional[UUID]
    name: str

    class Config:
        orm_mode = True


class Fos(BaseModel):
    id: Optional[UUID]
    name: str

    class Config:
        orm_mode = True


class Org(BaseModel):
    id: Optional[UUID]
    name: str

    class Config:
        orm_mode = True


class Text(BaseModel):
    id: Optional[UUID]
    title: str
    year: Optional[int] =  None
    n_citation: Optional[int] = 0
    abstract: Optional[str] = None
    venue_name: str
    keywords: Optional[List[Keyword]] = []
    orgs: Optional[Org] = None
    fos: Optional[List[Fos]] = []

    class Config:
        orm_mode = True
