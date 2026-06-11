import numpy as np

# ─── Матрица парных сравнений 17 критериев (лист МАИ Шум) ──────────────────
# Порядок: K3, K4, K5, K6, K7, K8, K9, K10, K11, K12, K13, K16, K20, K21, K22, K23, K25
PAIRWISE_CRITERIA = [
    [1,      1/3,   1/2,   3,     5,     1/4,   1/4,   3,     3,     3,     4,     1/4,   1/3,   5,     1/5,   4,     5    ],
    [3,      1,     2,     5,     7,     1/2,   1/2,   5,     5,     5,     6,     1/2,   1/2,   7,     1/3,   6,     7    ],
    [2,      1/2,   1,     4,     6,     1/3,   1/3,   4,     4,     4,     5,     1/3,   1/3,   6,     1/4,   5,     6    ],
    [1/3,    1/5,   1/4,   1,     3,     1/7,   1/7,   2,     2,     2,     3,     1/7,   1/6,   3,     1/8,   3,     3    ],
    [1/4,    1/7,   1/6,   1/3,   1,     1/8,   1/8,   1/2,   1/2,   1/2,   1,     1/8,   1/7,   2,     1/9,   1,     2    ],
    [4,      2,     3,     7,     8,     1,     1/2,   6,     6,     6,     7,     1/2,   1/2,   8,     1/3,   7,     8    ],
    [1/3,    2,     3,     7,     8,     2,     1,     6,     6,     6,     7,     1/2,   1/2,   8,     1/3,   7,     8    ],
    [1/3,    1/5,   1/4,   1/2,   2,     1/6,   1/6,   1,     1,     1,     2,     1/6,   1/5,   3,     1/7,   2,     3    ],
    [1/3,    1/5,   1/4,   1/2,   2,     1/6,   1/6,   1,     1,     1,     2,     1/6,   1/5,   3,     1/7,   2,     3    ],
    [1/3,    1/5,   1/4,   1/2,   2,     1/6,   1/6,   1,     1,     1,     2,     1/6,   1/5,   3,     1/7,   2,     3    ],
    [1/4,    1/6,   1/5,   1/3,   1,     1/7,   1/7,   1/2,   1/2,   1/2,   1,     1/7,   1/6,   2,     1/8,   1,     2    ],
    [4,      2,     3,     7,     8,     2,     2,     6,     6,     6,     7,     1,     1/2,   8,     1/3,   7,     8    ],
    [3,      2,     3,     6,     7,     2,     2,     5,     5,     5,     6,     2,     1,     7,     1/2,   6,     7    ],
    [1/5,    1/7,   1/6,   1/3,   1/2,   1/8,   1/8,   1/3,   1/3,   1/3,   1/2,   1/8,   1/7,   1,     1/9,   1/2,   1    ],
    [5,      3,     4,     8,     9,     3,     3,     7,     7,     7,     8,     3,     2,     9,     1,     8,     9    ],
    [1/4,    1/6,   1/5,   1/3,   1,     1/7,   1/7,   1/2,   1/2,   1/2,   1,     1/7,   1/6,   2,     1/8,   1,     2    ],
    [1/5,    1/7,   1/6,   1/3,   1/2,   1/8,   1/8,   1/3,   1/3,   1/3,   1/2,   1/8,   1/7,   1,     1/9,   1/2,   1    ],
]

RI_TABLE = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
            7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49, 11: 1.51,
            12: 1.54, 13: 1.56, 14: 1.57, 15: 1.58, 16: 1.59, 17: 1.60}

# Все 17 критериев из Excel (используемые в МАИ и TOPSIS)
CRITERIA_KEYS = [
    "k3_range", "k4_eff", "k5_torque",
    "k6_current", "k7_inertia", "k8_mass", "k9_price",
    "k10_ip", "k11_climate", "k12_cooling", "k13_mount",
    "k16_overload", "k20_insul",
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


def _calc_weights(matrix):
    A = np.array(matrix, dtype=float)
    n = A.shape[0]
    col_sums = A.sum(axis=0)
    norm_matrix = A / col_sums
    weights = norm_matrix.mean(axis=1)
    Aw = A @ weights
    lambda_max = float((Aw / weights).mean())
    CI = (lambda_max - n) / (n - 1)
    RI = RI_TABLE.get(n, 1.60)
    CR = CI / RI if RI > 0 else 0.0
    return weights, col_sums, norm_matrix, lambda_max, CI, RI, CR


def run_ahp(motors, custom_matrix=None):
    matrix = custom_matrix if custom_matrix else PAIRWISE_CRITERIA
    A = np.array(matrix, dtype=float)
    n_crit = len(CRITERIA_KEYS)

    w_crit, col_sums, norm_m, lam, CI, RI, CR = _calc_weights(matrix)

    n_alt = len(motors)
    U = np.array([
        [float(getattr(m, k) or 0) for k in CRITERIA_KEYS]
        for m in motors
    ])

    local_p = np.zeros((n_alt, n_crit))
    for j in range(n_crit):
        col = U[:, j]
        if DIRECTIONS[j] == "max":
            s = col.sum()
            local_p[:, j] = col / s if s > 0 else 1.0 / n_alt
        else:
            inv = 1.0 / (col + 1e-10)
            local_p[:, j] = inv / inv.sum()

    Zi = local_p @ w_crit

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
            "label":      f"Матрица критериев {n_crit}x{n_crit}",
            "lambda_max": round(lam, 4),
            "CI":         round(CI, 4),
            "RI":         round(RI, 4),
            "CR":         round(CR, 4),
            "consistent": CR < 0.1,
        }],
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
