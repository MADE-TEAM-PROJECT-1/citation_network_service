from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from app.core import config
import logging
from app.core.config import DATABASE_URL, SCHEMA_NAME, LOGS_DIR, LOGS_MESSAGE_FORMAT


logging.basicConfig(filename=LOGS_DIR, level=logging.DEBUG, format=LOGS_MESSAGE_FORMAT, filemode="a+")


engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)
metadata = MetaData(schema=SCHEMA_NAME)
logging.info(f"metadata is {metadata}")
Base = declarative_base(metadata=metadata)
