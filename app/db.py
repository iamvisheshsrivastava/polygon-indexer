from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# SQLite connection
DATABASE_URL = "sqlite:///./polygon_indexer.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Raw transactions table
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    block_number = Column(Integer, index=True)
    tx_hash = Column(String, unique=True, index=True)
    from_address = Column(String, index=True)
    to_address = Column(String, index=True)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Net flows table
class NetFlow(Base):
    __tablename__ = "net_flows"
    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, index=True)
    cumulative_inflow = Column(Float, default=0.0)
    cumulative_outflow = Column(Float, default=0.0)
    net_flow = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
