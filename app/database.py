from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

PG_DB_URL = "postgresql://postgres:adminla21@localhost/citation_network_db"

engine = create_engine(PG_DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData(schema='citation_network')
Base = declarative_base(metadata=metadata)
