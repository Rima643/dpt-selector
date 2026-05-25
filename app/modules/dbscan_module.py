import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Точно те же признаки что в ноутбуке Cell 2
CLUSTER_FEATURES = [
    "k1_power", "k2_eff", "k3_torque",
    "k5_mass", "k10_price"
]
CLUSTER_LABELS = [
    "K1 Мощность, кВт", "K2 КПД, %", "K3 Момент, Нм",
    "K5 Масса, кг", "K10 Цена, тыс.руб"
]

# Точно те же признаки PCA что в ноутбуке Cell 3
PCA_FEATURES = [
    "k1_power", "k2_eff", "k3_torque", "k4_current",
    "k5_mass", "k6_ip", "k7_cooling", "k8_inertia",
    "k9_mount", "k10_price", "k12_speed"
]
PCA_LABELS = [
    "K1 Мощность", "K2 КПД", "K3 Момент", "K4 Ток",
    "K5 Масса", "K6 IP", "K7 Охлаждение", "K8 Инерция",
    "K9 Монтаж", "K10 Цена", "K12 Скорость"
]

# Параметры DBSCAN из ноутбука
EPS = 1.5
MIN_SAMPLES = 3


def run_dbscan(motors):
    n = len(motors)
    motor_info = [
        {"id": m.id, "code": m.code, "name": m.name,
         "k1_power": m.k1_power}
        for m in motors
    ]

    # Матрица признаков для кластеризации
    X_raw = np.array([
        [float(getattr(m, k) or 0) for k in CLUSTER_FEATURES]
        for m in motors
    ])

    # Стандартизация
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # DBSCAN точно как в ноутбуке
    dbscan = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES, metric="euclidean")
    labels = dbscan.fit_predict(X_scaled).tolist()

    # PCA 2D для scatter-plot
    pca_2d = PCA(n_components=2)
    X_pca2 = pca_2d.fit_transform(X_scaled)

    # PCA полный по всем критериям (Cell 3 из ноутбука)
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

    # Количество компонент для порога 85% (как в ноутбуке)
    n_components_85 = int(np.argmax(
        np.array(cumulative) >= 0.85
    )) + 1

    # Нагрузки PC1 для ранжирования критериев
    loadings_pc1 = np.abs(pca_full.components_[0]).tolist()
    criteria_importance = sorted(
        [{"key": PCA_FEATURES[i], "label": PCA_LABELS[i],
          "loading": round(loadings_pc1[i], 4)}
         for i in range(len(PCA_FEATURES))],
        key=lambda x: x["loading"], reverse=True
    )

    # Группировка по кластерам
    clusters = {}
    for i, lbl in enumerate(labels):
        key = str(lbl)
        clusters.setdefault(key, []).append(motor_info[i])

    # PCA scatter данные
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
        # Шаги для отображения
        "steps": {
            "features":       CLUSTER_LABELS,
            "raw_matrix":     [[round(float(v), 4) for v in row]
                               for row in X_raw.tolist()],
            "scaled_matrix":  [[round(float(v), 4) for v in row]
                               for row in X_scaled.tolist()],
            "means":          [round(float(v), 4)
                               for v in scaler.mean_.tolist()],
            "stds":           [round(float(v), 4)
                               for v in scaler.scale_.tolist()],
            "labels_list":    labels,
            "motor_codes":    [m["code"] for m in motor_info],
        },
        "pca": {
            "scatter":            scatter_points,
            "pc1_var":            round(float(pca_2d.explained_variance_ratio_[0]), 4),
            "pc2_var":            round(float(pca_2d.explained_variance_ratio_[1]), 4),
            "explained_variance": [round(v, 4) for v in explained],
            "cumulative_variance":[round(v, 4) for v in cumulative],
            "n_components_85":    n_components_85,
            "criteria_importance":criteria_importance,
        },
    }