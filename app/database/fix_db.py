from database import engine, Base
from models import Motor  # добавь остальные модели если есть
from sqlalchemy import inspect, text

# Шаг 1: диагностика
insp = inspect(engine)
cols = [c['name'] for c in insp.get_columns('motors')]
print("Колонки в Render БД:")
print(cols)

# Шаг 2: дроп и пересоздание (раскомментируй после проверки шага 1)
# with engine.connect() as conn:
#     conn.execute(text("DROP TABLE IF EXISTS motors CASCADE"))
#     conn.commit()
# Base.metadata.create_all(engine)
# print("Таблица пересоздана успешно")