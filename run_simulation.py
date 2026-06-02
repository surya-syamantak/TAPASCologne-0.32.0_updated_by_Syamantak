import os
import sys
import csv
import statistics
import matplotlib.pyplot as plt

# =========================
# SUMO SETUP
# =========================

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please set the SUMO_HOME environment variable.")

import traci

# Create output folder
os.makedirs("output", exist_ok=True)

# =========================
# START SUMO
# =========================

sumoCmd = [
    "sumo-gui",
    "-c",
    "cologne6to8.sumocfg"
]

traci.start(sumoCmd)

# =========================
# RUN SIMULATION
# =========================

for step in range(500):
    traci.simulationStep()

print("\n===== SIMULATION SUMMARY =====")

sim_time = traci.simulation.getTime()

print("Simulation Time:", sim_time)

vehicle_ids = traci.vehicle.getIDList()
vehicle_count = len(vehicle_ids)

print("Active Vehicles:", vehicle_count)

# =========================
# SAVE VEHICLE DATA
# =========================

output_file = os.path.join(
    "output",
    "vehicle_data.csv"
)

speeds = []
waits = []

with open(output_file, mode="w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Vehicle_ID",
        "Speed_mps",
        "Speed_kmph",
        "Position_X",
        "Position_Y",
        "Waiting_Time_sec"
    ])

    for veh in vehicle_ids:

        speed = traci.vehicle.getSpeed(veh)
        speed_kmph = speed * 3.6

        x, y = traci.vehicle.getPosition(veh)

        wait = traci.vehicle.getWaitingTime(veh)

        speeds.append(speed)
        waits.append(wait)

        writer.writerow([
            veh,
            round(speed, 2),
            round(speed_kmph, 2),
            round(x, 2),
            round(y, 2),
            round(wait, 2)
        ])

print(f"\nVehicle data saved to: {output_file}")

# =========================
# TRAFFIC STATISTICS
# =========================

if vehicle_count > 0:

    avg_speed = statistics.mean(speeds)
    max_speed = max(speeds)
    min_speed = min(speeds)

    avg_wait = statistics.mean(waits)
    max_wait = max(waits)

    stopped_vehicles = sum(
        1 for s in speeds if s < 0.1
    )

    moving_vehicles = vehicle_count - stopped_vehicles

    congestion_ratio = (
        stopped_vehicles / vehicle_count
    ) * 100

    print("\n===== TRAFFIC STATISTICS =====")

    print(f"Total Vehicles       : {vehicle_count}")
    print(f"Moving Vehicles      : {moving_vehicles}")
    print(f"Stopped Vehicles     : {stopped_vehicles}")
    print(f"Congestion Ratio     : {congestion_ratio:.2f}%")

    print(f"Average Speed        : {avg_speed:.2f} m/s")
    print(f"Average Speed        : {avg_speed*3.6:.2f} km/h")

    print(f"Maximum Speed        : {max_speed:.2f} m/s")
    print(f"Minimum Speed        : {min_speed:.2f} m/s")

    print(f"Average Waiting Time : {avg_wait:.2f} sec")
    print(f"Maximum Waiting Time : {max_wait:.2f} sec")

# =========================
# TRAFFIC LIGHTS
# =========================

tls = traci.trafficlight.getIDList()

print(f"\nTraffic Lights: {len(tls)}")

# =========================
# GRAPH 1
# SUMMARY STATISTICS
# =========================

labels = [
    "Avg Speed\n(km/h)",
    "Max Speed\n(km/h)",
    "Avg Wait\n(sec)",
    "Max Wait\n(sec)",
    "Congestion\n(%)"
]

values = [
    avg_speed * 3.6,
    max_speed * 3.6,
    avg_wait,
    max_wait,
    congestion_ratio
]

plt.figure(figsize=(10, 6))

plt.bar(labels, values)

plt.title("Traffic Statistics Summary")
plt.ylabel("Value")

for i, v in enumerate(values):
    plt.text(i, v, f"{v:.2f}", ha="center")

plt.tight_layout()

plt.savefig(
    os.path.join(
        "output",
        "traffic_statistics_summary.png"
    )
)

# =========================
# GRAPH 2
# VEHICLE STATUS PIE CHART
# =========================

plt.figure(figsize=(7, 7))

plt.pie(
    [moving_vehicles, stopped_vehicles],
    labels=["Moving", "Stopped"],
    autopct="%1.1f%%"
)

plt.title("Vehicle Status Distribution")

plt.savefig(
    os.path.join(
        "output",
        "vehicle_status_distribution.png"
    )
)

# =========================
# GRAPH 3
# SPEED DISTRIBUTION
# =========================

speed_kmph = [
    s * 3.6
    for s in speeds
]

plt.figure(figsize=(10, 6))

plt.hist(
    speed_kmph,
    bins=20
)

plt.title("Vehicle Speed Distribution")

plt.xlabel("Speed (km/h)")
plt.ylabel("Number of Vehicles")

plt.grid(True)

plt.savefig(
    os.path.join(
        "output",
        "speed_distribution.png"
    )
)

# =========================
# GRAPH 4
# WAITING TIME DISTRIBUTION
# =========================

plt.figure(figsize=(10, 6))

plt.hist(
    waits,
    bins=20
)

plt.title("Waiting Time Distribution")

plt.xlabel("Waiting Time (sec)")
plt.ylabel("Number of Vehicles")

plt.grid(True)

plt.savefig(
    os.path.join(
        "output",
        "waiting_time_distribution.png"
    )
)

# =========================
# SHOW ALL PLOTS
# =========================

plt.show()

# =========================
# CLOSE SUMO
# =========================

traci.close()

print("\n===== FILES GENERATED =====")

print("output/vehicle_data.csv")
print("output/traffic_statistics_summary.png")
print("output/vehicle_status_distribution.png")
print("output/speed_distribution.png")
print("output/waiting_time_distribution.png")