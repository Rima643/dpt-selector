import numpy as np

# Матрица критериев 6x6 из Excel (лист МАИ Кластер 0, строки 31-36)
PAIRWISE_CRITERIA = [
    [1,    3,    2,    5,    7,    9   ],
    [1/3,  1,    0.5,  3,    5,    7   ],
    [0.5,  2,    1,    4,    6,    8   ],
    [0.2,  1/3,  0.25, 1,    2,    4   ],
    [1/7,  0.2,  1/6,  0.5,  1,    3   ],
    [1/9,  1/7,  0.125,0.25, 1/3,  1   ],
]

RI_TABLE = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12,
            6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}

# Критерии из Excel (K1,K2,K3,K4,K5,K10)
CRITERIA_KEYS   = ["k1_power","k2_eff","k3_torque",
                   "k4_current","k5_mass","k10_price"]
CRITERIA_LABELS = ["K1 Мощность","K2 КПД","K3 Момент",
                   "K4 Ток","K5 Масса","K10 Цена"]
DIRECTIONS      = ["max","max","max","min","min","min"]


def _calc_weights(matrix):
    A   = np.array(matrix, dtype=float)
    n   = A.shape[0]
    col_sums   = A.sum(axis=0)
    norm_matrix = A / col_sums
    weights     = norm_matrix.mean(axis=1)
    Aw          = A @ weights
    lambda_max  = float((Aw / weights).mean())
    CI          = (lambda_max - n) / (n - 1)
    RI          = RI_TABLE.get(n, 1.49)
    CR          = CI / RI if RI > 0 else 0.0
    return weights, col_sums, norm_matrix, lambda_max, CI, RI, CR


def run_ahp(motors, custom_matrix=None):
    matrix = custom_matrix if custom_matrix else PAIRWISE_CRITERIA
    A = np.array(matrix, dtype=float)
    n_crit = len(CRITERIA_KEYS)

    # Веса критериев
    w_crit, col_sums, norm_m, lam, CI, RI, CR = _calc_weights(matrix)

    # Данные двигателей
    n_alt = len(motors)
    U = np.array([
        [float(getattr(m, k) or 0) for k in CRITERIA_KEYS]
        for m in motors
    ])

    # Локальные приоритеты: нормировка по столбцу
    # Для max: v_i / sum(v); для min: (1/v_i) / sum(1/v)
    local_p = np.zeros((n_alt, n_crit))
    for j in range(n_crit):
        col = U[:, j]
        if DIRECTIONS[j] == "max":
            s = col.sum()
            local_p[:, j] = col / s if s > 0 else 1.0 / n_alt
        else:
            inv = 1.0 / (col + 1e-10)
            local_p[:, j] = inv / inv.sum()

    # Глобальные приоритеты Zi
    Zi = local_p @ w_crit

    # Ранжирование
    rank_order = np.argsort(Zi)[::-1]
    ranks = np.empty(n_alt, dtype=int)
    ranks[rank_order] = np.arange(1, n_alt + 1)

    ranking = []
    for i, m in enumerate(motors):
        ranking.append({
            "rank":  int(ranks[i]),
            "id":    m.id,
            "code":  m.code,
            "name":  m.name,
            "power": float(U[i, 0]),
            "Zi":    round(float(Zi[i]), 4),
            "local": {CRITERIA_KEYS[j]: round(float(local_p[i, j]), 4)
                      for j in range(n_crit)},
        })
    ranking.sort(key=lambda x: x["rank"])

    return {
        "all_consistent": CR < 0.1,
        "winner":    ranking[0],
        "ranking":   ranking,
        "consistency": [{
            "label":      "Матрица критериев 6x6",
            "lambda_max": round(lam, 4),
            "CI":         round(CI, 4),
            "RI":         round(RI, 4),
            "CR":         round(CR, 4),
            "consistent": CR < 0.1,
        }],
        # Все шаги для отображения на странице
        "steps": {
            "criteria_labels":   CRITERIA_LABELS,
            "criteria_keys":     CRITERIA_KEYS,
            "directions":        DIRECTIONS,
            "pairwise_matrix":   [[round(float(v), 4) for v in row]
                                  for row in A.tolist()],
            "col_sums":          [round(float(v), 4) for v in col_sums.tolist()],
            "normalized_matrix": [[round(float(v), 4) for v in row]
                                  for row in norm_m.tolist()],
            "weights":           [round(float(w), 4) for w in w_crit.tolist()],
            "lambda_max":        round(lam, 4),
            "CI":                round(CI, 4),
            "RI":                round(RI, 4),
            "CR":                round(CR, 4),
            "decision_matrix":   [[round(float(v), 4) for v in row]
                                  for row in U.tolist()],
            "local_priorities":  [[round(float(v), 4) for v in row]
                                  for row in local_p.tolist()],
            "global_scores":     [round(float(v), 4) for v in Zi.tolist()],
            "motor_codes":       [m.code for m in motors],
        },
    }