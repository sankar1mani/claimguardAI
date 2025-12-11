from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database import Base
from datetime import datetime

class Claim(Base):
    """Database model for Insurance Claims"""
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    merchant_name = Column(String)
    patient_name = Column(String)
    
    # Financials
    total_claimed = Column(Float)
    total_approved = Column(Float)
    total_deducted = Column(Float)
    
    # Status
    status = Column(String, index=True)
    
    # JSON Data (Store full result for analysis)
    full_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
