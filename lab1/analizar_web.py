import re
import json
from collections import defaultdict
from datetime import datetime

LOG_FILE = "lab1/access.log"
OUTPUT_FILE = "lab1/reporte_web.json"

line_pattern = re.compile(
    r'(\S+) \S+ \S+ \[(\d+/\w+/\d+):(\d+):(\d+):(\d+) .+\] '
    r'"(\w+) (\S+).*?" (\d+) \d+'
)

sqli_patterns = re.compile(r"UNION|SELECT|--|OR 1=1|'", re.I)

entries = []
with open(LOG_FILE) as f:
    for line in f:
        m = line_pattern.search(line)
        if m:
            ip = m.group(1)
            day = m.group(2)
            hour = int(m.group(3))
            minute = int(m.group(4))
            second = int(m.group(5))
            method = m.group(6)
            path = m.group(7)
            status = int(m.group(8))
            total_sec = hour * 3600 + minute * 60 + second
            day_sec = total_sec
            entries.append((ip, day, day_sec, method, path, status, line.strip()))

# --- Directory scanning detection ---
ip_times_paths = defaultdict(list)
for ip, day, ts, method, path, status, raw in entries:
    ip_times_paths[ip].append((ts, path))

scanning_ips = {}
for ip, vals in ip_times_paths.items():
    vals.sort()
    paths_by_time = defaultdict(set)
    for ts, path in vals:
        window_key = ts // 60
        paths_by_time[window_key].add(path)
    for window, paths in paths_by_time.items():
        if len(paths) > 15:
            scanning_ips[ip] = len(paths)
            break

if scanning_ips:
    print("=== DETECCION DE ESCANEO DE DIRECTORIOS ===")
    for ip, n in sorted(scanning_ips.items(), key=lambda x: -x[1]):
        print(f"  IP: {ip} - {n} rutas distintas en menos de 60s")

# --- 4xx and 5xx grouping ---
error_ips = defaultdict(lambda: {"4xx": 0, "5xx": 0, "total": 0})
for ip, day, ts, method, path, status, raw in entries:
    if status >= 400:
        error_ips[ip]["total"] += 1
        if 400 <= status < 500:
            error_ips[ip]["4xx"] += 1
        elif 500 <= status < 600:
            error_ips[ip]["5xx"] += 1

print("\n=== CODIGOS DE ERROR 4xx/5xx POR IP ===")
for ip, counts in sorted(error_ips.items(), key=lambda x: -x[1]["total"])[:15]:
    print(f"  IP: {ip:<20} 4xx: {counts['4xx']:<5} 5xx: {counts['5xx']:<5} Total: {counts['total']}")

# --- SQL Injection detection ---
sqli_entries = []
for ip, day, ts, method, path, status, raw in entries:
    if sqli_patterns.search(raw):
        sqli_entries.append({"ip": ip, "url": path, "status": status, "raw": raw.strip()})

if sqli_entries:
    print(f"\n=== POSIBLES INTENTOS DE SQL INJECTION ({len(sqli_entries)} detectados) ===")
    for e in sqli_entries[:10]:
        print(f"  IP: {e['ip']:<20} URL: {e['url']:<50} Status: {e['status']}")

# --- Build report ---
scanning_list = [{"ip": ip, "rutas_distintas": n} for ip, n in scanning_ips.items()]
error_list = [{"ip": ip, "4xx": c["4xx"], "5xx": c["5xx"], "total": c["total"]}
              for ip, c in sorted(error_ips.items(), key=lambda x: -x[1]["total"])]

reporte = {
    "fecha_analisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "escaneo_directorios": scanning_list,
    "errores_http_por_ip": error_list,
    "posibles_sqli": sqli_entries
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(reporte, f, indent=4, ensure_ascii=False)

print(f"\nReporte exportado a {OUTPUT_FILE}")
