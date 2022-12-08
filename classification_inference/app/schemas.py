from typing import List

from pydantic import BaseModel


class Predictions(BaseModel):
    predictions: List[str]


class Article(BaseModel):
    title: str
    abstract: str
