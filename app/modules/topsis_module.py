import numpy as np

# Критерии и веса из листа TOPSIS, строка 9 (w_j)
# Порядок: K3, K4, K5, K6, K7, K8, K9, K10, K11, K12, K13, K16, K20, K21, K22, K23, K25
CRITERIA_KEYS = [
    "k3_range", "k4_eff", "k5_torque",
    "k6_current", "k7_inertia", "k8_mass", "k9_price",
    "k10_ip", "k11_climat", "k12_cool", "k13_mount",
    "k16_load", "k20_insul",
    "k21_noise", "k22_mtbf", "k23_maint", "k25_repair",
]
CRITERIA_LABELS = [
    "K3 Диапазон D", "K4 КПД η, %", "K5 Момент M, Нм",
    "K6 Ток Iя, А", "K7 Инерция J", "K8 Масса, кг", "K9 Цена, тыс.руб",
    "K10 IP", "K11 Климат", "K12 Охлаждение", "K13 Монтаж IM",
    "K16 Перегрузка λ", "K20 Кл.изол.",
    "K21 Шум, дБА", "K22 MTBF, тыс.ч", "K23 ТО", "K25 Ремонт.",
]
DIRECTIONS = [
    "max", "max", "max",
    "min", "min", "min", "min",
    "max", "max", "max", "max",
    "max", "max",
    "min", "max", "min", "min",
]

# Веса из листа TOPSIS строка 9 (сумма = 1.0)
DEFAULT_WEIGHTS = [
    0.0437, 0.1098, 0.1697,
    0.0421, 0.0371, 0.0371, 0.1098,
    0.0151, 0.0081, 0.0081, 0.0044,
    0.1697, 0.1098,
    0.0208, 0.0437, 0.0234, 0.0476,
]


def run_topsis(motors, custom_weights=None,
               ideal_best_custom=None, ideal_worst_custom=None):
    n = len(motors)
    m = len(CRITERIA_KEYS)
    w = np.array(custom_weights if custom_weights else DEFAULT_WEIGHTS,
                 dtype=float)

    U = np.zeros((n, m))
    for i, motor in enumerate(motors):
        for j, key in enumerate(CRITERIA_KEYS):
            U[i, j] = float(getattr(motor, key) or 0)

    # Шаг 1: нормировка
    U_sq = U ** 2
    col_sq_sum = U_sq.sum(axis=0)
    col_norms = np.sqrt(col_sq_sum)
    col_norms[col_norms == 0] = 1e-10
    R = U / col_norms

    # Шаг 2: взвешенная нормированная матрица
    V = R * w

    # Шаг 3: идеальное и анти-идеальное решения
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

    # Шаг 4: расстояния
    diff_star = (V - A_star) ** 2
    diff_neg = (V - A_neg) ** 2
    S_star = np.sqrt(diff_star.sum(axis=1))
    S_neg = np.sqrt(diff_neg.sum(axis=1))

    # Шаг 5: коэффициент близости
    denom = S_star + S_neg
    denom[denom == 0] = 1e-10
    C = S_neg / denom

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
