from pydantic import BaseModel
from typing import List


class ReceiveId(BaseModel):
    id: List[str]


class Predictions(BaseModel):
    neighbors: List[str]
