import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Признаки для кластеризации (количественные, хорошо различают альтернативы)
CLUSTER_FEATURES = [
    "k3_range", "k4_eff", "k5_torque",
    "k8_mass", "k9_price"
]
CLUSTER_LABELS = [
    "K3 Диапазон D", "K4 КПД η, %", "K5 Момент M, Нм",
    "K8 Масса, кг", "K9 Цена, тыс.руб"
]

# Все количественные признаки для PCA (исключены пороговые K14,K15,K17,K24,K26)
PCA_FEATURES = [
    "k1_power", "k3_range", "k4_eff", "k5_torque",
    "k6_current", "k7_inertia", "k8_mass", "k9_price",
    "k10_ip", "k12_cool", "k13_mount",
    "k16_load", "k20_insul", "k21_noise", "k22_mtbf",
    "k23_maint", "k25_repair",
]
PCA_LABELS = [
    "K1 Мощность", "K3 Диапазон", "K4 КПД", "K5 Момент",
    "K6 Ток", "K7 Инерция", "K8 Масса", "K9 Цена",
    "K10 IP", "K12 Охлажд.", "K13 Монтаж",
    "K16 Перегрузка", "K20 Кл.изол.", "K21 Шум", "K22 MTBF",
    "K23 ТО", "K25 Ремонт.",
]

EPS = 1.5
MIN_SAMPLES = 3


def run_dbscan(motors):
    n = len(motors)
    motor_info = [
        {"id": m.id, "code": m.code, "name": m.name,
         "k1_power": m.k1_power}
        for m in motors
    ]

    X_raw = np.array([
        [float(getattr(m, k) or 0) for k in CLUSTER_FEATURES]
        for m in motors
    ])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    dbscan = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES, metric="euclidean")
    labels = dbscan.fit_predict(X_scaled).tolist()

    pca_2d = PCA(n_components=2)
    pca_2d.fit_transform(X_scaled)

    X_pca_full = StandardScaler().fit_transform(
        np.array([
            [float(getattr(m, k) or 0) for k in PCA_FEATURES]
            for m in motors
        ])
    )
    pca_full = PCA()
    pca_full.fit(X_pca_full)
    explained = pca_full.explained_variance_ratio_.tolist()
    cumulative = np.cumsum(pca_full.explained_variance_ratio_).tolist()

    n_components_85 = int(np.argmax(np.array(cumulative) >= 0.85)) + 1

    loadings_pc1 = np.abs(pca_full.components_[0]).tolist()
    criteria_importance = sorted(
        [{"key": PCA_FEATURES[i], "label": PCA_LABELS[i],
          "loading": round(loadings_pc1[i], 4)}
         for i in range(len(PCA_FEATURES))],
        key=lambda x: x["loading"], reverse=True
    )

    # PCA scatter по признакам кластеризации
    X_pca2 = PCA(n_components=2).fit_transform(X_scaled)

    clusters = {}
    for i, lbl in enumerate(labels):
        key = str(lbl)
        clusters.setdefault(key, []).append(motor_info[i])

    scatter_points = [
        {
            "x":     round(float(X_pca2[i, 0]), 4),
            "y":     round(float(X_pca2[i, 1]), 4),
            "label": labels[i],
            "code":  motor_info[i]["code"],
            "name":  motor_info[i]["name"],
        }
        for i in range(n)
    ]

    return {
        "eps":         EPS,
        "min_samples": MIN_SAMPLES,
        "n_motors":    n,
        "n_clusters":  len(set(labels) - {-1}),
        "n_noise":     labels.count(-1),
        "labels":      {motor_info[i]["id"]: labels[i] for i in range(n)},
        "clusters":    clusters,
        "steps": {
            "features":      CLUSTER_LABELS,
            "raw_matrix":    [[round(float(v), 4) for v in row]
                              for row in X_raw.tolist()],
            "scaled_matrix": [[round(float(v), 4) for v in row]
                              for row in X_scaled.tolist()],
            "means":         [round(float(v), 4)
                              for v in scaler.mean_.tolist()],
            "stds":          [round(float(v), 4)
                              for v in scaler.scale_.tolist()],
            "labels_list":   labels,
            "motor_codes":   [m["code"] for m in motor_info],
        },
        "pca": {
            "scatter":             scatter_points,
            "pc1_var":             round(float(pca_2d.explained_variance_ratio_[0]), 4),
            "pc2_var":             round(float(pca_2d.explained_variance_ratio_[1]), 4),
            "explained_variance":  [round(v, 4) for v in explained],
            "cumulative_variance": [round(v, 4) for v in cumulative],
            "n_components_85":     n_components_85,
            "criteria_importance": criteria_importance,
        },
    }