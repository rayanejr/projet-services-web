from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from .params import TradParams, DictParams, UpdateDict
from .response import IndexResponse, postTradResponse, DictResponse, DictWithLinesResponse
from .models import Trad, Dicts, DictLine, Base
from .database import SessionLocal, engine
from typing import List

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

    for line in params.lines:
        new_line = DictLine(key=line.key, value=line.value, dict_id=new_dict.id)
        db.add(new_line)

    db.commit()
    return new_dict


@app.get('/dicts/all', response_model=List[DictWithLinesResponse])
def get_dicts(db: Session = Depends(get_db)):
    dicts = db.query(Dicts).all()
    dicts_lines = []

    if dicts is None:
        raise HTTPException(status_code=404, detail="Il n'y a aucun dictionnaire")
    
    for dict in dicts:
        lines = db.query(DictLine).filter(DictLine.dict_id == dict.id).all()
        dicts_lines.append({
            "id": dict.id,
            "name": dict.name,
            "lines": lines
        })

    return dicts_lines

@app.get('/dict/{dict_id}', response_model=DictWithLinesResponse)
def get_dict(dict_id: int, db: Session = Depends(get_db)):
    dict_data = db.query(Dicts).filter(Dicts.id == dict_id).first()

    if dict_data is None:
        raise HTTPException(status_code=404, detail="Le dictionnaire n'existe pas")
    
    lines = db.query(DictLine).filter(DictLine.dict_id == dict_id).all()
    return {'id': dict_data.id, 'name': dict_data.name, 'lines': lines}

@app.put('/dict/{dict_id}/update', response_model=DictWithLinesResponse)
def update_dict(dict_id: int, params: UpdateDict, db: Session = Depends(get_db)):
    dict_update = db.query(Dicts).filter(Dicts.id == dict_id).first()
    if dict_update is None:
        raise HTTPException(status_code=404, detail="Le dictionnaire n'existe pas")

    dict_update.name = params.name

    for line_param in params.lines:
        if line_param.id:
            line_update = db.query(DictLine).filter(DictLine.id == line_param.id, DictLine.dict_id == dict_id).first()
            if line_update:
                line_update.key = line_param.key
                line_update.value = line_param.value
        else:
            new_line = DictLine(key=line_param.key, value=line_param.value, dict_id=dict_id)
            db.add(new_line)

    db.commit()
    return dict_update

@app.delete('/dict/{dict_id}', response_model=DictResponse)
def delete_dict(dict_id: int, db: Session = Depends(get_db)):
    dict_delete = db.query(Dicts).filter(Dicts.id == dict_id).first()

    if dict_delete is None:
        raise HTTPException(status_code=404, detail="Le dictionnaire n'existe pas")
    
    db.query(DictLine).filter(DictLine.dict_id == dict_id).delete()
    db.query(Trad).filter(Trad.dict_id == dict_id).delete()
    db.delete(dict_delete)
    db.commit()
    return dict_delete

@app.post('/translate', response_model=postTradResponse)
def translate_word(params: TradParams, db: Session = Depends(get_db)):
    dict = db.query(Dicts).filter(Dicts.id == params.dict_id).first()

    if dict is None:
        raise HTTPException(status_code=404, detail="Le dictionnaire n'existe pas")
    
    mot_trad = ""

    for letter in params.word:
        if letter.isspace():
            mot_trad += " "
        else:
            translation_entry = db.query(DictLine).filter(
                func.lower(DictLine.key) == func.lower(letter), 
                DictLine.dict_id == dict.id
            ).first()
            mot_trad += translation_entry.value if translation_entry else "?"

    new_trad = Trad(word=params.word, trad=mot_trad.strip(), dict_id=dict.id)
    db.add(new_trad)
    db.commit()
    return {'word': params.word, 'dict_id': dict.id, 'trad': mot_trad.strip()}