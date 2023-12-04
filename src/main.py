from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Trad, Dicts, DictLine, Base
from .params import TradParams, DictParams, UpdateDictParams, DictLineParams
from .response import IndexResponse,postTradResponse, DictResponse, AllDictsResponse
from .database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=IndexResponse)
def index():
    return {'msg': 'Bienvenue dans mon API de Traduction !'}

@app.post('/dict', response_model=DictResponse)
def create_dict(params: DictParams, db: Session = Depends(get_db)):
    new_dict = Dicts(name=params.name)
    db.add(new_dict)
    db.commit()
    db.refresh(new_dict)
    return new_dict

@app.get('/dicts', response_model=AllDictsResponse)
def get_dicts(db: Session = Depends(get_db)):
    dicts = db.query(Dicts).all()
    return {'dicts': dicts}

@app.get('/dict/{dict_id}', response_model=DictResponse)
def get_dict(dict_id: int, db: Session = Depends(get_db)):
    dict = db.query(Dicts).filter(Dicts.id == dict_id).first()
    if dict is None:
        raise HTTPException(status_code=404, detail="Le dictionnaire n'existe pas dans la bdd")
    return dict

@app.put('/dict/{dict_id}', response_model=DictResponse)
def update_dict(dict_id: int, params: UpdateDictParams, db: Session = Depends(get_db)):
    dict = db.query(Dicts).filter(Dicts.id == dict_id).first()
    if dict is None:
        raise HTTPException(status_code=404, detail="Le dictionnaire n'existe pas dans la bdd")
    dict.name = params.name
    db.commit()
    return dict

@app.post('/dict/line', response_model=DictResponse)
def add_dictline(params: DictLineParams, db: Session = Depends(get_db)):
    new_line = DictLine(key=params.key, value=params.value, dict_id=params.dict_id)
    db.add(new_line)
    db.commit()
    db.refresh(new_line)
    return new_line

@app.post('/translate', response_model=postTradResponse)
def translate_word(params: TradParams, db: Session = Depends(get_db)):
    dict = db.query(Dicts).filter(Dicts.id == params.dict_id).first()
    if dict is None:
        raise HTTPException(status_code=404, detail="Le dictionnaire n'existe pas")

    translated_word = ""
    for letter in params.word:
        if letter.isspace():
            translated_word += " "
            continue

        translation_entry = db.query(DictLine).filter(
            func.lower(DictLine.key) == func.lower(letter), 
            DictLine.dict_id == dict.id
        ).first()

        translated_word += translation_entry.value if translation_entry else "?"

    new_trad = Trad(word=params.word, trad=translated_word.strip(), dict_id=dict.id)
    db.add(new_trad)
    db.commit()

    return {
        'word': params.word,
        'dict_id': dict.id,
        'trad': translated_word.strip()
    }



