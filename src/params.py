from pydantic import BaseModel
from typing import List

class TradParams(BaseModel):
    word: str
    dict_id: int
    
class DictLineParams(BaseModel):
    key: str
    value: str
    dict_id: int

class DictParams(BaseModel):
    name: str

class UpdateDictParams(BaseModel):
    name: str



    
