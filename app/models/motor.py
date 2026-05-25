from sqlalchemy import Column, Integer, Float, String
from app.database.database import Base

class Motor(Base):
    __tablename__ = "motors"

    id          = Column(Integer, primary_key=True, index=True)
    code        = Column(String(50), nullable=False)
    name        = Column(String(255), nullable=False)
    k1_power    = Column(Float)   # мощность кВт max
    k2_eff      = Column(Float)   # КПД % max
    k3_torque   = Column(Float)   # момент Нм max
    k4_current  = Column(Float)   # ток А min
    k5_mass     = Column(Float)   # масса кг min
    k6_ip       = Column(Integer) # IP 23/44
    k7_cooling  = Column(Integer) # охлаждение 1/3
    k8_inertia  = Column(Float)   # инерция кг*м2
    k9_mount    = Column(Integer) # монтаж
    k10_price   = Column(Float)   # цена тыс.руб min
    k12_speed   = Column(Float)   # скорость об/мин