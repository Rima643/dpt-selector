from fastapi import FastAPI
from app.database.database import Base, engine, SessionLocal
from app.api import motors, analysis, pages, reports
from app.models.motor import Motor

Base.metadata.create_all(bind=engine)

# Автозаполнение: запускается при старте сервера.
# Если в БД нет двигателя с кодом "A1" — удаляем старые и вставляем новые.
def _seed():
    from fill_db import MOTORS
    db = SessionLocal()
    try:
        exists = db.query(Motor).filter(Motor.code == "A1").first()
        if exists:
            print("[seed] Новые данные уже загружены, пропускаем")
            return
        deleted = db.query(Motor).delete()
        print(f"[seed] Удалено старых записей: {deleted}")
        for row in MOTORS:
            (code, name,
             k1, k2, k3, k4, k5, k6, k7, k8, k9,
             k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20,
             k21, k22, k23, k24, k25, k26) = row
            db.add(Motor(
                code=code, name=name,
                k1_power=k1,   k2_speed=k2,   k3_range=k3,
                k4_eff=k4,     k5_torque=k5,  k6_current=k6,
                k7_inertia=k7, k8_mass=k8,    k9_price=k9,
                k10_ip=k10,    k11_climat=k11, k12_cool=k12,
                k13_mount=k13, k14_spark=k14, k15_revers=k15,
                k16_load=k16,  k17_mode=k17,  k18_env=k18,
                k19_mech=k19,  k20_insul=k20, k21_noise=k21,
                k22_mtbf=k22,  k23_maint=k23, k24_excit=k24,
                k25_repair=k25, k26_compat=k26,
            ))
        db.commit()
        print(f"[seed] Добавлено {len(MOTORS)} двигателей")
    except Exception as e:
        db.rollback()
        print(f"[seed] Ошибка: {e}")
    finally:
        db.close()

_seed()

app = FastAPI(
    title="DPT Selector",
    description="Многокритериальный выбор ДПТ",
    version="1.0.0"
)

app.include_router(pages.router)
app.include_router(motors.router,   prefix="/api/motors",   tags=["Motors"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(reports.router,  prefix="/api",          tags=["Reports"])
