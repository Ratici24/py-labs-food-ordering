import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg://foodapp:foodpass@localhost:5435/foodapp"
RAW_DSN = "dbname=foodapp user=foodapp password=foodpass host=localhost port=5435"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def raw_conn():
    return psycopg.connect(RAW_DSN)
