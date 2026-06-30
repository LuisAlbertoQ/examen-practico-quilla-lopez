import sys
import pandas as pd
import numpy as np
import joblib

if len(sys.argv) < 2:
    print("Uso: python predecir.py <archivo_csv>")
    sys.exit(1)

csv_path = sys.argv[1]

model = joblib.load("lab3/modelo_anomalias.pkl")
scaler = joblib.load("lab3/scaler.pkl")
feature_cols = joblib.load("lab3/feature_cols.pkl")

df = pd.read_csv(csv_path)

df["ratio_bytes"] = df["bytes_sent"] / (df["bytes_recv"] + 1)
df["bytes_por_segundo"] = (df["bytes_sent"] + df["bytes_recv"]) / (df["duration_sec"] + 0.001)
df["total_bytes"] = df["bytes_sent"] + df["bytes_recv"]

for col in feature_cols:
    if col not in df.columns:
        df[col] = 0

X = scaler.transform(df[feature_cols])
preds = model.predict(X)
scores = model.decision_function(X)

anomalies = df[preds == -1].copy()
anomalies["anomaly_score"] = scores[preds == -1]

anomalies = anomalies.sort_values("anomaly_score")

print(f"Total registros analizados: {len(df)}")
print(f"Anomalias detectadas: {len(anomalies)}")
print()
if len(anomalies) > 0:
    print(f"{'Src IP':<20} {'Dst IP':<20} {'Protocolo':<10} {'Bytes Env':<12} {'Score':<12}")
    print("-" * 80)
    for _, row in anomalies.iterrows():
        print(f"{str(row.get('src_ip','')):<20} {str(row.get('dst_ip','')):<20} "
              f"{str(row.get('protocol','')):<10} {row.get('bytes_sent',0):<12} "
              f"{row['anomaly_score']:<12.4f}")
else:
    print("No se detectaron anomalias.")
