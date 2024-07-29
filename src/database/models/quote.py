from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from ..db import Base

class Quote(Base):
    __tablename__ = "quote"

    avito_id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    category = Column(String)
    rub_price = Column(Float)
    price_ratio = Column(Float)
    status = Column(String)
    title = Column(String)
    url = Column(String, unique=True)
    last_time_update = Column(DateTime)
    quote_status = Column(Boolean, default=True)