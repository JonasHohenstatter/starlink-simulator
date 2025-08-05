import matplotlib.pyplot as plt

# Read CSV file manually
times = []
latencies = []

path = "histogram.csv"

with open(path, "r") as f:
    for line in f:
        # Skip empty or malformed lines
        if not line.strip():
            continue
        parts = line.strip().split(",")
        if len(parts) != 2:
            continue
        try:
            time = float(parts[0])
            latency = float(parts[1])
            times.append(time)
            latencies.append(latency)
        except ValueError:
            continue  # skip lines with invalid data

# Plot
plt.figure(figsize=(10, 5))
plt.plot(times, latencies, marker='o', linestyle='-', color='blue')
plt.title("Latency over Time")
plt.xlabel("Time (s)")
plt.ylabel("Latency (µs or ms)")
plt.grid(True)
plt.tight_layout()
plt.savefig("/root/latency_plot.jpg", dpi=300)