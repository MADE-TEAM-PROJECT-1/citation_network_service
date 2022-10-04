from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core import config

from app.core.config import DATABASE_URL, SCHEMA_NAME

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)
metadata = MetaData(schema=SCHEMA_NAME)
Base = declarative_base(metadata=metadata)
