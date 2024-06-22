from sqlalchemy import Column, Integer, String
from database import Base

class UserDetails(Base):
    __tablename__ = "user_details"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
