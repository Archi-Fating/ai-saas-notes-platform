from sqlalchemy import Column,Integer,String,Text,ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(Integer,primary_key=True,index=True)
    role = Column(String,nullable=False)
    content = Column(Text,nullable=False)
    user_id = Column(Integer,ForeignKey("users.id"))
    user = relationship("User")