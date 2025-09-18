import argparse
import matplotlib.pyplot as plt
import os
import datetime
import csv

def plot_combined_data(latency_filename, loss_filename, folder_name):
    """
    Reads latency and loss data, synchronizes them, and generates a
    plot with high-res latency and per-second aggregated packet loss.
    """
    # --- 1a. Read latency data ---
    latency_data = {}
    try:
        with open(latency_filename, 'r') as f:
            for line in f:
                if not line.strip(): continue
                timestamp, latency = line.strip().split(',')
                latency_data[int(timestamp)] = float(latency)
    except FileNotFoundError:
        print(f"Error: Latency file not found at '{latency_filename}'")
        return

    # --- 1b. Read loss data ---
    loss_data = {}
    try:
        with open(loss_filename, 'r') as f:
            for line in f:
                if not line.strip(): continue
                timestamp, lost, received = line.strip().split(',')
                loss_data[int(timestamp)] = (int(lost), int(received))
    except FileNotFoundError:
        print(f"Error: Loss file not found at '{loss_filename}'")
        return

    # --- 2. Determine the effective start time ---
    start_time = 0
    sorted_latency_timestamps = sorted(latency_data.keys())
    for ts in sorted_latency_timestamps:
        if round(latency_data[ts] / 1_000_000) > 0:
            start_time = ts
            break

    if start_time == 0:
        print("Warning: Could not determine a valid start time.")
        start_time = sorted_latency_timestamps[0] if sorted_latency_timestamps else 0

    # --- 3. Synchronize data ---
    common_timestamps = sorted(latency_data.keys() & loss_data.keys())
    final_timestamps = [t for t in common_timestamps if t >= start_time]

    if not final_timestamps:
        print("Error: No overlapping data found between the files.")
        return

    # --- 4. Aggregate loss data per second ---
    loss_per_second = {}
    for t in final_timestamps:
        second_bucket = int((t - start_time) / 1_000_000_000.0)
        if second_bucket not in loss_per_second:
            loss_per_second[second_bucket] = {'lost': 0, 'received': 0}
        lost_packets, received_packets = loss_data[t]
        loss_per_second[second_bucket]['lost'] += lost_packets
        loss_per_second[second_bucket]['received'] += received_packets

    # --- 5. Prepare final data lists for plotting ---
    time_in_seconds_latency = [(t - start_time) / 1_000_000_000.0 for t in final_timestamps]
    latencies_in_ms = [round(latency_data[t]) / 1_000_000 for t in final_timestamps]
    
    time_in_seconds_loss = sorted(loss_per_second.keys())
    loss_percentages = []
    for sec in time_in_seconds_loss:
        bucket = loss_per_second[sec]
        total_packets = bucket['lost'] + bucket['received']
        percentage = (bucket['lost'] / total_packets * 100) if total_packets > 0 else 0
        loss_percentages.append(percentage)
        
    # --- NEW: Filter loss points to only include those > 0 ---
    filtered_loss_points = [(t, p) for t, p in zip(time_in_seconds_loss, loss_percentages)]
    
    plot_time_loss, plot_percentages_loss = [], []
    if filtered_loss_points:
        plot_time_loss, plot_percentages_loss = zip(*filtered_loss_points)

    # --- 6. Create the plot ---
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Latency
    color1 = 'blue'
    ax1.set_xlabel('Time from Start (seconds)', fontsize=12)
    ax1.set_ylabel('Latency (ms)', fontsize=12, color=color1)
    ax1.plot(time_in_seconds_latency, latencies_in_ms, linewidth=2, color=color1, label='Latency')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax1.set_ylim(min(latencies_in_ms) - 1, max(latencies_in_ms) + 1)

    ax2 = ax1.twinx()
    color2 = 'red'
    ax2.set_ylabel('Packet Loss (%)', fontsize=12, color=color2)
    ax2.plot(plot_time_loss, plot_percentages_loss, color=color2, linestyle='--', label='Packet Loss (>0%)')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 100)
    
    os.makedirs(folder_name, exist_ok=True)
    
    with open(f'{folder_name}/latency_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time (s)', 'Latency (ms)']) # Write header
        writer.writerows(zip(time_in_seconds_latency, latencies_in_ms))
    print("✅ Latency data saved to 'latency_data.csv'")

    # Save loss data
    with open(f'{folder_name}/loss_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time (s)', 'Loss (%)']) # Write header
        writer.writerows(zip(plot_time_loss, plot_percentages_loss))
    print("✅ Packet loss data saved to 'loss_data.csv'")

    # --- 7. Finalize and save the plot ---
    plt.title('Latency and Packet Loss Over Time', fontsize=16)
    fig.tight_layout()
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

    output_filename = 'latency_and_loss_over_time.png'
    plt.savefig(f"{folder_name}/{output_filename}")
    print(f"✅ Graph successfully generated and saved as '{output_filename}' to '{folder_name}'")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a combined latency and loss graph from data files.')
    parser.add_argument('latency_file', type=str, help='Path to the latency data file.')
    parser.add_argument('loss_file', type=str, help='Path to the packet loss data file.')
    parser.add_argument('folder_name', type=str, help='Path to output dir.')
    args = parser.parse_args()
    plot_combined_data(args.latency_file, args.loss_file, args.folder_name)