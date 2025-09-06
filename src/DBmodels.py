from sqlalchemy import Column, String, Integer
from db import Base


class Phone(Base):
    __tablename__ = "phone"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String)
    current_date = Column(String)
    current_time = Column(String)
    click_order = Column(Integer)
