from fastapi import FastAPI, Body, Depends, Query, HTTPException
from pydantic import BaseModel, ValidationError, Field
from sqlalchemy.orm import Session
from typing import Annotated
from DBmodels import Phone
from db import get_db, Base, engine
from math import ceil


app = FastAPI()

Base.metadata.create_all(bind=engine)


class DataNumber(BaseModel):
    number: Annotated[str, Field(..., title='Номер телефона РФ может начинатся либо с 8, либо с +7', min_length=11, max_length=12)]
    currentDate: str
    currentTime: str
    clickOrder: int


class DataNumberResponse(DataNumber):
    id: int

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    records: list[DataNumberResponse]
    total: int
    skip: int
    limit: int
    total_pages: int
    current_page: int


@app.get("/NumberList", response_model=PaginatedResponse)
def get_num_list(db: Session = Depends(get_db),
                skip: int = Query(0, description="Количество пропускаемых записей", ge=0),
                limit: int = Query(10, description="Количество записей, выведенных на странице", ge=1, le=100)
                 ):
    """phones_list = db.query(Phone).offset(skip).limit(limit).all()
    return [DataNumberResponse(
            id=phone.id,
            number=phone.number,
            currentDate=phone.current_date,
            currentTime=phone.current_time,
            clickOrder=phone.click_order
        ) for phone in phones_list]"""
    try:
        total = db.query(Phone).count()

        phones_list = db.query(Phone).order_by(Phone.id).offset(skip).limit(limit).all()

        records = [
            DataNumberResponse(
                id=phone.id,
                number=phone.number,
                currentDate=phone.current_date,
                currentTime=phone.current_time,
                clickOrder=phone.click_order
            )
            for phone in phones_list
        ]

        total_pages = ceil(total / limit) if total > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return PaginatedResponse(
            records=records,
            total=total,
            skip=skip,
            limit=limit,
            total_pages=total_pages,
            current_page=current_page
        )
    except ValidationError as e:
        print(f"Ошибка валидации: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())


@app.post("/addPhoneNumber", response_model=DataNumberResponse)
def add_phone_num(data: Annotated[DataNumber, Body(embed=True)], db: Session = Depends(get_db)):
    try:
        print(f"Полученные данные: {data.dict()}")
        phone_db = Phone(number=data.number, current_date=data.currentDate,
                         current_time=data.currentTime, click_order=data.clickOrder)
        db.add(phone_db)
        db.commit()
        db.refresh(phone_db)
        return DataNumberResponse(
            id=phone_db.id,
            number=phone_db.number,
            currentDate=phone_db.current_date,
            currentTime=phone_db.current_time,
            clickOrder=phone_db.click_order
        )
    except ValidationError as e:
        print(f"Ошибка валидации: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
