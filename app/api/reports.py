from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io

from app.database.database import get_db
from app.models.motor import Motor

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/export")
def export_report(data: dict, db: Session = Depends(get_db)):
    try:
        motor_ids = data.get("motor_ids", [])
        topsis_ranking = data.get("topsis_ranking", [])
        ahp_ranking = data.get("ahp_ranking", [])
        project_name = data.get("project_name", "DPT_Selection")

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # TOPSIS
            if topsis_ranking:
                pd.DataFrame(topsis_ranking).to_excel(
                    writer, sheet_name="TOPSIS_Ранжирование", index=False
                )

            # AHP
            if ahp_ranking:
                pd.DataFrame(ahp_ranking).to_excel(
                    writer, sheet_name="AHP_Ранжирование", index=False
                )

            # Все выбранные двигатели
            if motor_ids:
                motors = db.query(Motor).filter(Motor.id.in_(motor_ids)).all()
                motor_data = [{
                    "ID": m.id,
                    "Код": m.code,
                    "Название": m.name,
                    "Мощность (кВт)": m.k1_power,
                    "КПД (%)": m.k2_eff,
                    "Момент (Нм)": m.k3_torque,
                    "Масса (кг)": m.k5_mass,
                    "Цена (тыс.руб)": m.k10_price,
                } for m in motors]
                pd.DataFrame(motor_data).to_excel(
                    writer, sheet_name="Выбранные_двигатели", index=False
                )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={project_name}.xlsx"
            }
        )

    except Exception as e:
        raise HTTPException(500, f"Ошибка при создании отчёта: {str(e)}")