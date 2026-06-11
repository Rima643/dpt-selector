from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.motor import Motor

router = APIRouter()


@router.get("/")
def get_all(db: Session = Depends(get_db)):
    return db.query(Motor).order_by(Motor.k1_power).all()


@router.get("/filter")
def filter_motors(
    power_min:  float = Query(0),
    power_max:  float = Query(9999),
    ip:         Optional[int] = Query(None),
    cooling:    Optional[int] = Query(None),
    mount:      Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Motor).filter(
        Motor.k1_power >= power_min,
        Motor.k1_power <= power_max
    )
    if ip is not None:
        q = q.filter(Motor.k10_ip == ip)
    if cooling is not None:
        q = q.filter(Motor.k12_cooling == cooling)
    if mount is not None:
        q = q.filter(Motor.k13_mount == mount)
    results = q.order_by(Motor.k1_power).all()
    return {"count": len(results), "motors": results}


@router.put("/{motor_id}")
def update_motor(motor_id: int, data: dict, db: Session = Depends(get_db)):
    motor = db.query(Motor).filter(Motor.id == motor_id).first()
    if not motor:
        raise HTTPException(404, "Не найден")
    for field, value in data.items():
        if hasattr(motor, field):
            setattr(motor, field, value)
    db.commit()
    db.refresh(motor)
    return motor


@router.delete("/{motor_id}")
def delete_motor(motor_id: int, db: Session = Depends(get_db)):
    motor = db.query(Motor).filter(Motor.id == motor_id).first()
    if not motor:
        raise HTTPException(404, "Не найден")
    db.delete(motor)
    db.commit()
    return {"deleted": motor_id}
