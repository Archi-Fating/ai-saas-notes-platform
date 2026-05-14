from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    content = Column(Text)
    user_id = Column(Integer,ForeignKey("users.id"))
    owner = relationship("User",back_populates="notes")
    folder_id=Column(Integer,ForeignKey("folders.id"),nullable=True)
    folder=relationship("Folder",back_populates="notes")