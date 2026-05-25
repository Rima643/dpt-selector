from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database.database import Base

class Project(Base):
    __tablename__ = "projects"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(255), nullable=False)
    description  = Column(String(500), default="")
    created_at   = Column(DateTime, server_default=func.now())
    motor_ids    = Column(JSON, default=[])
    weights      = Column(JSON, default={})
    status       = Column(String(50), default="new")
    cluster_data = Column(JSON, default={})
    ahp_data     = Column(JSON, default={})
    topsis_data  = Column(JSON, default={})