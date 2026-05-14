from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

from app.config import DATABASE_URL

engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
#Changes are NOT automatically saved
#Prevents automatic DB syncing before queries.
Base=declarative_base()