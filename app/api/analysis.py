from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database.database import get_db
from app.models.motor import Motor
from app.modules.dbscan_module import run_dbscan
from app.modules.ahp_module import run_ahp
from app.modules.topsis_module import run_topsis

router = APIRouter()


class ClusterRequest(BaseModel):
    motor_ids: List[int]


class AHPRequest(BaseModel):
    motor_ids: List[int]
    custom_matrix: Optional[List[List[float]]] = None


class TOPSISRequest(BaseModel):
    motor_ids: List[int]
    custom_weights: Optional[List[float]] = None
    ideal_best: Optional[List[float]] = None
    ideal_worst: Optional[List[float]] = None


@router.post("/cluster")
def cluster(req: ClusterRequest, db: Session = Depends(get_db)):
    motors = db.query(Motor).filter(Motor.id.in_(req.motor_ids)).all()
    if len(motors) < 3:
        return {"error": "Нужно минимум 3 двигателя"}
    return run_dbscan(motors)


@router.post("/ahp")
def ahp(req: AHPRequest, db: Session = Depends(get_db)):
    motors = db.query(Motor).filter(Motor.id.in_(req.motor_ids)).all()
    if len(motors) < 2:
        return {"error": "Нужно минимум 2 двигателя"}
    return run_ahp(motors, req.custom_matrix)


@router.post("/topsis")
def topsis(req: TOPSISRequest, db: Session = Depends(get_db)):
    motors = db.query(Motor).filter(Motor.id.in_(req.motor_ids)).all()
    if len(motors) < 2:
        return {"error": "Нужно минимум 2 финалиста"}
    return run_topsis(motors, req.custom_weights,
                      req.ideal_best, req.ideal_worst)