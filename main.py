from fastapi import FastAPI
from app.database.database import Base, engine
from app.api import motors, analysis, pages, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DPT Selector",
    description="Многокритериальный выбор ДПТ",
    version="1.0.0"
)

app.include_router(pages.router)
app.include_router(motors.router,   prefix="/api/motors",   tags=["Motors"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(reports.router,  prefix="/api",          tags=["Reports"])