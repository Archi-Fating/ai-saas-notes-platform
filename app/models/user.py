from sqlalchemy import Column,Integer,String
from app.database import Base
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    notes=relationship("Note",back_populates="owner")
    folders=relationship("Folder",back_populates="owner")