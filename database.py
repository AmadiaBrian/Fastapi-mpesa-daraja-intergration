from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database
DATABASE_URL = "sqlite:///database.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Transaction model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    merchant_request_id = Column(String, unique=True, index=True)
    checkout_request_id = Column(String, index=True)
    result_code = Column(Integer)
    result_desc = Column(String)
    amount = Column(Float, nullable=True)
    mpesa_receipt = Column(String, nullable=True)
    transaction_date = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    account_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    callback_data = Column(Text, nullable=True)  # Store full callback JSON

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
