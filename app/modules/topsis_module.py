import numpy as np

# Критерии и веса точно из листа TOPSIS Excel строка 10
CRITERIA_KEYS   = ["k1_power","k2_eff","k3_torque",
                   "k4_current","k5_mass","k10_price"]
CRITERIA_LABELS = ["K1 Мощность, кВт","K2 КПД, %","K3 Момент, Нм",
                   "K4 Ток якоря, А","K5 Масса, кг","K10 Стоимость, тыс.р."]
DIRECTIONS      = ["max","max","max","min","min","min"]

# Веса из Excel строка 10: 0.3943, 0.1807, 0.2694, 0.0802, 0.0492, 0.0263
DEFAULT_WEIGHTS = [0.3943, 0.1807, 0.2694, 0.0802, 0.0492, 0.0263]


def run_topsis(motors, custom_weights=None,
               ideal_best_custom=None, ideal_worst_custom=None):
    n = len(motors)
    m = len(CRITERIA_KEYS)
    w = np.array(custom_weights if custom_weights else DEFAULT_WEIGHTS,
                 dtype=float)

    # Матрица решений U
    U = np.zeros((n, m))
    for i, motor in enumerate(motors):
        for j, key in enumerate(CRITERIA_KEYS):
            U[i, j] = float(getattr(motor, key) or 0)

    # Шаг 1: квадраты и корни (как в Excel строки 12-20)
    U_sq    = U ** 2
    col_sq_sum = U_sq.sum(axis=0)
    col_norms  = np.sqrt(col_sq_sum)
    col_norms[col_norms == 0] = 1e-10

    # Нормированная матрица r_ij = u_ij / sqrt(sum u^2)
    R = U / col_norms

    # Шаг 2: взвешенная нормированная матрица v_ij = r_ij * w_j
    V = R * w

    # Шаг 3: идеальное A* и антиидеальное A- (строки 41-42 Excel)
    if ideal_best_custom:
        A_star = np.array(ideal_best_custom, dtype=float)
    else:
        A_star = np.array([
            V[:, j].max() if DIRECTIONS[j] == "max" else V[:, j].min()
            for j in range(m)
        ])

    if ideal_worst_custom:
        A_neg = np.array(ideal_worst_custom, dtype=float)
    else:
        A_neg = np.array([
            V[:, j].min() if DIRECTIONS[j] == "max" else V[:, j].max()
            for j in range(m)
        ])

    # Шаг 4: расстояния S* и S- (строки 47-59 Excel)
    diff_star = (V - A_star) ** 2
    diff_neg  = (V - A_neg)  ** 2
    S_star = np.sqrt(diff_star.sum(axis=1))
    S_neg  = np.sqrt(diff_neg.sum(axis=1))

    # Шаг 5: коэффициент близости C* (строки 62-67 Excel)
    denom = S_star + S_neg
    denom[denom == 0] = 1e-10
    C = S_neg / denom

    # Ранжирование
    rank_order = np.argsort(C)[::-1]
    ranks = np.empty(n, dtype=int)
    ranks[rank_order] = np.arange(1, n + 1)

    ranking = []
    for i, motor in enumerate(motors):
        ranking.append({
            "rank":   int(ranks[i]),
            "id":     motor.id,
            "code":   motor.code,
            "name":   motor.name,
            "power":  float(U[i, 0]),
            "S_star": round(float(S_star[i]), 6),
            "S_neg":  round(float(S_neg[i]),  6),
            "C_star": round(float(C[i]),       4),
        })
    ranking.sort(key=lambda x: x["rank"])

    return {
        "winner":  ranking[0],
        "ranking": ranking,
        # Все шаги для отображения
        "steps": {
            "criteria_labels":   CRITERIA_LABELS,
            "criteria_keys":     CRITERIA_KEYS,
            "directions":        DIRECTIONS,
            "weights":           w.tolist(),
            "decision_matrix":   [[round(float(v), 4) for v in row]
                                  for row in U.tolist()],
            "squared_matrix":    [[round(float(v), 4) for v in row]
                                  for row in U_sq.tolist()],
            "col_sq_sums":       [round(float(v), 4) for v in col_sq_sum.tolist()],
            "col_norms":         [round(float(v), 6) for v in col_norms.tolist()],
            "normalized_matrix": [[round(float(v), 6) for v in row]
                                  for row in R.tolist()],
            "weighted_matrix":   [[round(float(v), 6) for v in row]
                                  for row in V.tolist()],
            "A_star":            [round(float(v), 6) for v in A_star.tolist()],
            "A_neg":             [round(float(v), 6) for v in A_neg.tolist()],
            "diff_star":         [[round(float(v), 6) for v in row]
                                  for row in diff_star.tolist()],
            "diff_neg":          [[round(float(v), 6) for v in row]
                                  for row in diff_neg.tolist()],
            "S_star_list":       [round(float(v), 6) for v in S_star.tolist()],
            "S_neg_list":        [round(float(v), 6) for v in S_neg.tolist()],
            "C_star_list":       [round(float(v), 4) for v in C.tolist()],
            "motor_codes":       [motor.code for motor in motors],
        },
    }