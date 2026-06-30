import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import numpy as np

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# --- SSH data ---
failed_pattern = re.compile(r"Failed password.*from (\S+)")
ip_counter = Counter()

with open("lab1/auth.log") as f:
    for line in f:
        m = failed_pattern.search(line)
        if m:
            ip_counter[m.group(1)] += 1

top10 = ip_counter.most_common(10)
ips = [ip for ip, _ in top10]
counts = [c for _, c in top10]

# Graph 1: Top 10 IPs SSH
plt.figure()
colors = sns.color_palette("Reds_r", len(ips))
plt.barh(ips, counts, color=colors)
plt.xlabel("Intentos fallidos")
plt.title("Top 10 IPs con mas intentos fallidos SSH")
plt.gca().invert_yaxis()
for i, v in enumerate(counts):
    plt.text(v + 1, i, str(v), va="center")
plt.tight_layout()
plt.savefig("lab1/graficas/top10_ssh.png", dpi=150)
plt.close()
print("[OK] top10_ssh.png generado")

# --- HTTP data ---
line_pattern = re.compile(
    r"(\S+) \S+ \S+ \[(\d+/\w+/\d+):(\d+):(\d+):(\d+) .+\] "
    r'"(\w+) (\S+).*?" (\d+) \d+'
)

hour_counter = Counter()
hour_status = defaultdict(lambda: Counter())

with open("lab1/access.log") as f:
    for line in f:
        m = line_pattern.search(line)
        if m:
            hour = int(m.group(3))
            status = int(m.group(8))
            hour_counter[hour] += 1
            hour_status[hour][status] += 1

hours = sorted(hour_counter.keys())
reqs_per_hour = [hour_counter[h] for h in hours]

# Graph 2: Timeline HTTP
plt.figure()
plt.plot(hours, reqs_per_hour, marker="o", linestyle="-", color="b")
plt.xticks(range(0, 24))
plt.xlabel("Hora del dia")
plt.ylabel("Numero de peticiones")
plt.title("Peticiones HTTP por hora")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("lab1/graficas/timeline_http.png", dpi=150)
plt.close()
print("[OK] timeline_http.png generado")

# Graph 3: Heatmap
all_hours = list(range(24))
target_status = [200, 301, 404, 500]
heatmap_data = np.zeros((len(target_status), 24))

for i, status in enumerate(target_status):
    for h in all_hours:
        heatmap_data[i, h] = hour_status[h].get(status, 0)

plt.figure(figsize=(14, 5))
sns.heatmap(heatmap_data, xticklabels=all_hours, yticklabels=target_status,
            annot=True, fmt=".0f", cmap="YlOrRd", cbar_kws={"label": "Peticiones"})
plt.xlabel("Hora del dia")
plt.ylabel("Codigo de respuesta")
plt.title("Peticiones HTTP por hora y codigo de respuesta")
plt.tight_layout()
plt.savefig("lab1/graficas/heatmap_http.png", dpi=150)
plt.close()
print("[OK] heatmap_http.png generado")
