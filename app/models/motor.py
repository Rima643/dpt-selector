from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base


class Motor(Base):
    __tablename__ = "motors"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # A1, A2, ...
    name = Column(String)                            # ELDIN Д-21М, ...

    # K1-K26 строго по Excel
    k1_power   = Column(Float)   # K1  Номинальная мощность P, кВт
    k2_speed   = Column(Float)   # K2  Номинальная частота вращения nном, об/мин
    k3_range   = Column(Float)   # K3  Диапазон регулирования D = nmax/nном
    k4_eff     = Column(Float)   # K4  КПД η, %
    k5_torque  = Column(Float)   # K5  Номинальный момент M, Н·м
    k6_current = Column(Float)   # K6  Ток якоря Iя, А
    k7_inertia = Column(Float)   # K7  Момент инерции якоря J, кг·м²
    k8_mass    = Column(Float)   # K8  Масса, кг
    k9_price   = Column(Float)   # K9  Цена, тыс. руб.
    k10_ip     = Column(Float)   # K10 Степень защиты IP, балл
    k11_climat = Column(Float)   # K11 Климатическое исполнение, балл
    k12_cool   = Column(Float)   # K12 Способ охлаждения IC, балл
    k13_mount  = Column(Float)   # K13 Монтажное исполнение IM, балл
    k14_spark  = Column(Float)   # K14 Искрозащищённость, балл
    k15_revers = Column(Float)   # K15 Регулировочно-реверсивные свойства, балл
    k16_load   = Column(Float)   # K16 Перегрузочная способность λ
    k17_mode   = Column(String)  # K17 Режим работы (S1..S8)
    k18_env    = Column(Float)   # K18 Условия эксплуатации (свод), балл
    k19_mech   = Column(Float)   # K19 Механизмы, балл
    k20_insul  = Column(Float)   # K20 Класс нагревостойкости изоляции, балл
    k21_noise  = Column(Float)   # K21 Уровень шума, дБА
    k22_mtbf   = Column(Float)   # K22 MTBF, тыс. ч
    k23_maint  = Column(Float)   # K23 Требовательность к ТО, балл
    k24_excit  = Column(Float)   # K24 Тип возбуждения (порог)
    k25_repair = Column(Float)   # K25 Ремонтопригодность, балл
    k26_compat = Column(Float)   # K26 Совместимость с СУ (порог)