import sys
sys.path.insert(0, r'C:\Users\rimad\PycharmProjects\PythonProject1')

from app.database.database import engine, Base
from app.models.motor import Motor
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS motors CASCADE'))
    conn.commit()

Base.metadata.create_all(engine)
print('Tablica peresоzdana uspeshno')
