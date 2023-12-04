from pydantic import BaseModel
from typing import List

class IndexResponse(BaseModel):
    msg: str

class getTradResponse(BaseModel):
    word: str

class postTradResponse(BaseModel):
    word: str
    dict_id: int
    trad: str

class DictResponse(BaseModel):
    id: int
    name: str

class AllDictsResponse(BaseModel):
    dicts: List[DictResponse]
