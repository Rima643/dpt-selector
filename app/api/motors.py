from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
import io

from app.database.database import get_db
from app.models.motor import Motor

router = APIRouter()


@router.get("/")
def get_all(db: Session = Depends(get_db)):
    return db.query(Motor).order_by(Motor.k1_power).all()


@router.get("/filter")
def filter_motors(
    power_min: float = Query(0),
    power_max: float = Query(9999),
    ip: Optional[int] = Query(None),
    cooling: Optional[int] = Query(None),
    mount: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Motor).filter(
        Motor.k1_power >= power_min,
        Motor.k1_power <= power_max
    )
    if ip is not None:
        q = q.filter(Motor.k6_ip == ip)
    if cooling is not None:
        q = q.filter(Motor.k7_cooling == cooling)
    if mount is not None:
        q = q.filter(Motor.k9_mount == mount)
    results = q.order_by(Motor.k1_power).all()
    return {"count": len(results), "motors": results}


@router.post("/import")
async def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(400, "Файл должен быть .xlsx, .xls или .csv")

    contents = await file.read()
    try:
        if file.filename.endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding="utf-8")
            except Exception:
                df = pd.read_csv(io.BytesIO(contents), encoding="cp1251")
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(400, f"Ошибка чтения файла: {e}")

    added, errors = 0, []
    col_map = {
        "code": ["code", "код", "Code"],
        "name": ["name", "название", "Name", "Альтернатива"],
        "k1_power": ["k1_power", "K1", "k1", "мощность"],
        "k2_eff": ["k2_eff", "K2", "k2", "кпд"],
        "k3_torque": ["k3_torque", "K3", "k3", "момент"],
        "k4_current": ["k4_current", "K4", "k4", "ток"],
        "k5_mass": ["k5_mass", "K5", "k5", "масса"],
        "k6_ip": ["k6_ip", "K6", "k6", "ip"],
        "k7_cooling": ["k7_cooling", "K7", "k7", "охлаждение"],
        "k8_inertia": ["k8_inertia", "K8", "k8", "инерция"],
        "k9_mount": ["k9_mount", "K9", "k9", "монтаж"],
        "k10_price": ["k10_price", "K10", "k10", "цена"],
        "k12_speed": ["k12_speed", "K12", "k12", "скорость"],
    }

    def find_col(field):
        for alias in col_map[field]:
            for c in df.columns:
                if c.strip().lower() == alias.lower():
                    return c
        return None

    for idx, row in df.iterrows():
        try:
            code_col = find_col("code")
            name_col = find_col("name")
            if not code_col or not name_col:
                errors.append("Не найдены столбцы code/name")
                break
            code = str(row[code_col]).strip()
            name = str(row[name_col]).strip()
            if not code or not name or code == "nan":
                continue
            if db.query(Motor).filter(Motor.code == code).first():
                errors.append(f"{code}: уже существует")
                continue

            def get_val(field, default=0):
                c = find_col(field)
                if c is None:
                    return default
                v = row[c]
                return float(v) if v is not None and str(v) != "nan" else default

            motor = Motor(
                code=code, name=name,
                k1_power=get_val("k1_power"),
                k2_eff=get_val("k2_eff"),
                k3_torque=get_val("k3_torque"),
                k4_current=get_val("k4_current"),
                k5_mass=get_val("k5_mass"),
                k6_ip=int(get_val("k6_ip", 23)),
                k7_cooling=int(get_val("k7_cooling", 1)),
                k8_inertia=get_val("k8_inertia"),
                k9_mount=int(get_val("k9_mount", 2)),
                k10_price=get_val("k10_price"),
                k12_speed=get_val("k12_speed", 1500),
            )
            db.add(motor)
            added += 1
        except Exception as e:
            errors.append(f"Строка {idx+2}: {e}")

    db.commit()
    return {"added": added, "errors": errors}


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