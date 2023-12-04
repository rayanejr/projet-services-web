from pydantic import BaseModel
from typing import List

class postTradResponse(BaseModel):
    word: str
    dict_id: int
    trad: str

class DictResponse(BaseModel):
    id: int
    name: str

class AllDictsResponse(BaseModel):
    dicts: List[DictResponse]

class IndexResponse(BaseModel):
    msg: str