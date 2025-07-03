from sqlalchemy import Column, Integer, String

from ..db import Base


class User(Base):

    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    user_name = Column(String, nullable=False)
    
    email_address = Column(String, nullable=False, unique=True)
    
    password = Column(String, nullable=False)
