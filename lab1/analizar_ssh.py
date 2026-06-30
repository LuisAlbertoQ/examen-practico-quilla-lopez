import re
import json
from collections import defaultdict
from datetime import datetime

LOG_FILE = "lab1/auth.log"
OUTPUT_FILE = "lab1/reporte_ssh.json"

failed_pattern = re.compile(r"Failed password.*from (\S+)")
ip_counter = defaultdict(int)

with open(LOG_FILE) as f:
    for line in f:
        m = failed_pattern.search(line)
        if m:
            ip_counter[m.group(1)] += 1

sorted_ips = sorted(ip_counter.items(), key=lambda x: -x[1])

print("=== TOP 10 IPs - Intentos Fallidos SSH ===")
print(f"{'IP':<20} {'Intentos':<10}")
print("-" * 30)
for ip, count in sorted_ips[:10]:
    print(f"{ip:<20} {count:<10}")

print("\n=== ALERTAS ===")
suspicious = []
for ip, count in sorted_ips:
    alerta = count > 50
    if alerta:
        print(f"[ALERTA] IP: {ip} - {count} intentos fallidos - Posible ataque de fuerza bruta")
    suspicious.append({"ip": ip, "intentos": count, "alerta": alerta})

reporte = {
    "fecha_analisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_intentos_fallidos": sum(ip_counter.values()),
    "ips_sospechosas": suspicious
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(reporte, f, indent=4, ensure_ascii=False)

print(f"\nReporte exportado a {OUTPUT_FILE}")
