import random
import matplotlib.pyplot as plt
import numpy as np
import csv
import subprocess
import pandas as pd
import pickle
from keras.models import load_model

lanes = [3,2,3,2]
default_timings = [[30,30,30,30]]
# default_timings = [[60,30,60,30]]
# default_timings = [[60,60,60,60]]
# default_timings = [[90,60,90,60]]
# default_timings = [[90,90,90,90]]


def get_optimal_timings(density):
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('models/svm_models.pkl', 'rb') as f:
        models = pickle.load(f)
    lstm_model = load_model('models/lstm_model.h5')
    density = [[0,0,0,0,0,0,0,0,0,0,0,0], density]
    X_new_scaled = scaler.transform(density)

    svm_outputs_new = []
    for i in range(len(models)):
        svm_outputs_new.append(models[i].predict(X_new_scaled))
    svm_outputs_new = np.array(svm_outputs_new).T
    X_new_lstm = np.reshape(svm_outputs_new, (svm_outputs_new.shape[0], 1, svm_outputs_new.shape[1]))

    y_pred_new = lstm_model.predict(X_new_lstm)
    timings = y_pred_new[1]
    timings = [int(timing) for timing in timings]

    return timings

def map_density(value):
    if value <= 0.3: return 1
    elif 0.3 < value <= 0.5: return 2
    elif 0.5 < value <= 0.7: return 3
    elif  0.7 < value <= 1: return 4
    return 0

def calculate_densities(vehicles):
    density = []
    for i in range(4):
        density.append(vehicles[i]/(300 * lanes[i]))
    mapped_density = [map_density(i) for i in density]
    final_density = [mapped_density[i] for j in range(3) for i in range(4)]
    return final_density

def find_new_timings(vehicles):
    density = calculate_densities(vehicles)
    for i in range(12):
        if density[i] == 0:
            return None
    new_times = get_optimal_timings(tuple(density))
    return new_times

def single_side(total_time, green_time, vehicle_count, inflow, lane_type):
    time_elapsed = 2
    vehicle_count += 2 * inflow
    for i in range(green_time):
        time_elapsed += 1
        total_time += 1
        vehicle_count += inflow
        if time_elapsed <= 3:
            vehicle_count -= min(vehicle_count, lane_type)
        else:
            if lane_type == 2:
                vehicle_count -= min(vehicle_count, random.randint(1,3))
            elif lane_type == 3:
                vehicle_count -= min(vehicle_count, random.randint(2,4))
    inflow = random.randint(inflow, inflow+2) % 5
    return total_time, vehicle_count

def single_cycle(times, vehicles, inflow, default):
    total_cycle_time = 0
    for i in range(4):
        if times is None:
            break
        green_time = times[i]
        lane_vehicle_count = vehicles[i]
        lane_type = lanes[i]
        total_cycle_time, vehicles[i] = single_side(total_cycle_time, green_time, lane_vehicle_count, inflow, lane_type)
        if default:
            continue
        times = find_new_timings(vehicles)
    return total_cycle_time, vehicles, times

def run_simulation_ours(times, vehicles):
    total_time = 0
    inflow = random.randint(0,4)
    default = False
    while total_time < 86400 and times is not None:
        cycle_time, vehicles, times = single_cycle(times, vehicles, inflow, default)
        total_time += cycle_time
        for i in range(4):
            if vehicles[i] > 0:
                break
            if i == 3:
                return total_time
    return total_time

def run_simulation_default(times, vehicles):
    total_time = 0
    inflow = random.randint(0,4)
    default = True
    while total_time < 86400 and times != None:
        cycle_time, vehicles, _ = single_cycle(times, vehicles, inflow, default)
        total_time += cycle_time
        for i in range(4):
            if vehicles[i] > 0:
                break
            if i == 3:
                return total_time
    return total_time

def check_simulation(times, vehicles, run):
    clearance_time = run(times, vehicles)
    if clearance_time >= 86400:
        return (False, 86400, vehicles)
    elif times is None:
        return (False, clearance_time, vehicles)
    return (True, clearance_time, vehicles)

def compare_clearance_times(times, vehicles):
    cleared, clearance_time, vehicles_at_end = check_simulation(times, vehicles, run_simulation_ours)
    outputs = {}
    for time in default_timings:
        current_cleared, current_clearance_time, current_vehicles_at_end = check_simulation(time, vehicles, run_simulation_default)
        if cleared:
            if current_cleared:
                if current_clearance_time < clearance_time:
                    outputs[tuple(time)] = (False, cleared, current_cleared, clearance_time - current_clearance_time)
                else:
                    outputs[tuple(time)] = (True, cleared, current_cleared, current_clearance_time - clearance_time)
            else:
                outputs[tuple(time)] = (True, cleared, current_cleared, clearance_time)
        else:
            if current_cleared:
                outputs[tuple(time)] = (False, cleared, current_cleared, current_clearance_time)
            else:
                if clearance_time < current_clearance_time:
                    outputs[tuple(time)] = (False, cleared, current_cleared, current_clearance_time - clearance_time)
                else:
                    outputs[tuple(time)] = (True, cleared, current_cleared, clearance_time - current_clearance_time)
    return outputs

def create_random_initial_vehicle_list():
    vehicles = []
    for i in range(4):
        vehicles.append(random.randint(0, 300))
        vehicles[-1] *= lanes[i]
    return vehicles

def plot(
    our_score, total_iterations, 
    cleared_quicker_count, cleared_quicker_value,
    default_cleared_quicker_count, default_cleared_quicker_value,
    cleared_and_default_failed_count, cleared_and_default_failed_value,
    failed_and_default_cleared_count, failed_and_default_cleared_value,
    congested_quicker_count, congested_quicker_value,
    default_congested_quicker_count, default_congested_quicker_value
):
    base_path = 'graphs/30s/90-60-90-60/'

    labels = ['Our Method Better', 'Default Method Better']
    counts = [our_score, total_iterations - our_score]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Better Count")
    plt.title("Method Overview Comparison")
    plt.savefig(base_path + 'method_overview_comparison.png')

    labels = ['Our Method Cleared', 'Default Method Cleared']
    counts = [cleared_quicker_count + default_cleared_quicker_count + cleared_and_default_failed_count, cleared_quicker_count + default_cleared_quicker_count + failed_and_default_cleared_count]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Cleared Count")
    plt.title("Times Cleared Comparison")
    plt.savefig(base_path + 'times_cleared_comparison.png')
    
    labels = ['Our Method Better', 'Default Method Better']
    counts = [cleared_quicker_count, default_cleared_quicker_count]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Better Count")
    plt.title("Times Better Comparison (When Both Cleared)")
    plt.savefig(base_path + 'times_better_comparison_both_cleared.png')

    labels = ['Our Method Better Avg Value', 'Default Method Better Avg Value']
    counts = [cleared_quicker_value / max(1, cleared_quicker_count), default_cleared_quicker_value / max(1, default_cleared_quicker_count)]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Better Avg Value")
    plt.title("Value Better Comparison (When Both Cleared)")
    plt.savefig(base_path + 'value_better_comparison_both_cleared.png')

    labels = ['Our Method Better', 'Default Method Better']
    counts = [cleared_and_default_failed_count, failed_and_default_cleared_count]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Better Count")
    plt.title("Times Better Comparison (When One Cleared)")
    plt.savefig(base_path + 'times_better_comparison_one_cleared.png')

    labels = ['Our Method Better Avg Value', 'Default Method Better Avg Value']
    counts = [cleared_and_default_failed_value / max(1, cleared_and_default_failed_count), failed_and_default_cleared_value / max(1, failed_and_default_cleared_count)]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Better Avg Value")
    plt.title("Value Better Comparison (When One Cleared)")
    plt.savefig(base_path + 'value_better_comparison_one_cleared.png')

    labels = ['Our Method Better', 'Default Method Better']
    counts = [default_congested_quicker_count, congested_quicker_count]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Better Count")
    plt.title("Congested Later Comparison (When Congested)")
    plt.savefig(base_path + 'congested_later_comparison.png')

    labels = ['Our Method Better Avg Value', 'Default Method Better Avg Value']
    counts = [default_congested_quicker_value / max(1, default_congested_quicker_count), congested_quicker_value / max(1, congested_quicker_count)]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'orange'])
    plt.xlabel("Method")
    plt.ylabel("Better Avg Value")
    plt.title("Congested Later Comparison (When Congested)")
    plt.savefig(base_path + 'congested_later_comparison.png')

def analyse_and_store(    
    our_score, total_iterations, 
    cleared_quicker_count, cleared_quicker_value,
    default_cleared_quicker_count, default_cleared_quicker_value,
    cleared_and_default_failed_count, cleared_and_default_failed_value,
    failed_and_default_cleared_count, failed_and_default_cleared_value,
    congested_quicker_count, congested_quicker_value,
    default_congested_quicker_count, default_congested_quicker_value
):
    with open('results/30s_label.txt', 'a') as file:
        file.write("\n")
        file.write("==================================================\n")
        file.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        file.write("\n")
        file.write(f"Test Results for {total_iterations} iterations against {default_timings}\n")
        file.write("\n")
        file.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        file.write("==================================================\n")
        file.write("\n")
        file.write("-----------------------------------------------\n")
        file.write("-----------------------------------------------\n")
        file.write(f"Our Score: {our_score}\n")
        file.write(f"Total Iterations: {total_iterations}\n")
        file.write(f"Cleared Quicker Count: {cleared_quicker_count}\n")
        file.write(f"Cleared Quicker Value: {cleared_quicker_value}\n")
        file.write(f"Default Cleared Quicker Count: {default_cleared_quicker_count}\n")
        file.write(f"Default Cleared Quicker Value: {default_cleared_quicker_value}\n")
        file.write(f"Cleared and Default Failed Count: {cleared_and_default_failed_count}\n")
        file.write(f"Cleared and Default Failed Value: {cleared_and_default_failed_value}\n")
        file.write(f"Failed and Default Cleared Count: {failed_and_default_cleared_count}\n")
        file.write(f"Failed and Default Cleared Value: {failed_and_default_cleared_value}\n")
        file.write(f"Congested Quicker Count: {congested_quicker_count}\n")
        file.write(f"Congested Quicker Value: {congested_quicker_value}\n")
        file.write(f"Default Congested Quicker Count: {default_congested_quicker_count}\n")
        file.write(f"Default Congested Quicker Value: {default_congested_quicker_value}\n")
        file.write("-----------------------------------------------\n")
        file.write("-----------------------------------------------\n")
        file.write("\n")
        file.write("-----------------------------------------------\n")
        file.write("-----------------------------------------------\n")
        file.write(f"Times Our Model is Better: {our_score}\n")
        file.write(f"Percentage Our Model is Better: {our_score / total_iterations}\n")
        file.write(f"Times Default Timing is Better: {total_iterations - our_score}\n")
        file.write(f"Percentage Default Timing is Better: {(total_iterations - our_score) / total_iterations}\n")
        file.write("-----------------------------------------------\n")
        file.write("-----------------------------------------------\n")
        file.write(f"Times Our Model Cleared: {cleared_quicker_count + cleared_and_default_failed_count}\n")
        file.write(f"Percentage Our Model Cleared: {(cleared_quicker_count + cleared_and_default_failed_count) / total_iterations}\n")
        file.write(f"Times Default Timing Cleared: {cleared_quicker_count + failed_and_default_cleared_count}\n")
        file.write(f"Percentage Default Timing Cleared: {(cleared_quicker_count + failed_and_default_cleared_count) / total_iterations}\n")
        file.write(f"When Both Cleared: {cleared_quicker_count + default_cleared_quicker_count}\n")
        file.write(f"When One Cleared: {cleared_and_default_failed_count + failed_and_default_cleared_count}\n")
        file.write("-----------------------------------------------\n")
        file.write(f"When Our Model Cleared - Average Time Taken: {cleared_quicker_value / max(1, cleared_quicker_count) + cleared_and_default_failed_value / max(1, cleared_and_default_failed_count)}\n")
        file.write(f"When Default Timing Cleared - Average Time Taken: {default_cleared_quicker_value / max(1, default_cleared_quicker_count) + failed_and_default_cleared_value / max(1, failed_and_default_cleared_count)}\n")
        file.write("-----------------------------------------------\n")
        file.write("-----------------------------------------------\n")
        file.write(f"Times Ours Congested: {failed_and_default_cleared_count + congested_quicker_count + default_congested_quicker_count}\n")
        file.write(f"Times Default Congested: {cleared_quicker_count + congested_quicker_count + default_congested_quicker_count}\n")
        file.write("-----------------------------------------------\n")
        file.write(f"Ours Congested - Average Time Taken: {failed_and_default_cleared_value / max(1, failed_and_default_cleared_count) + congested_quicker_value / max(1, congested_quicker_count)}\n")
        file.write(f"Default Congested - Average Time Taken: {cleared_quicker_value / max(1, cleared_quicker_count) + default_congested_quicker_value / max(1, default_congested_quicker_count)}\n")
        file.write("-----------------------------------------------\n")
        file.write("-----------------------------------------------\n")
        file.write("\n\n")

    data = [
        ["Our Score", our_score],
        ["Total Iterations", total_iterations],
        ["Cleared Quicker Count", cleared_quicker_count],
        ["Cleared Quicker Value", cleared_quicker_value],
        ["Default Cleared Quicker Count", default_cleared_quicker_count],
        ["Default Cleared Quicker Value", default_cleared_quicker_value],
        ["Cleared and Default Failed Count", cleared_and_default_failed_count],
        ["Cleared and Default Failed Value", cleared_and_default_failed_value],
        ["Failed and Default Cleared Count", failed_and_default_cleared_count],
        ["Failed and Default Cleared Value", failed_and_default_cleared_value],
        ["Congested Quicker Count", congested_quicker_count],
        ["Congested Quicker Value", congested_quicker_value],
        ["Default Congested Quicker Count", default_congested_quicker_count],
        ["Default Congested Quicker Value", default_congested_quicker_value]
    ]

    with open('results/30s_90-60-90-60.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        writer.writerows(data)

def main():
    our_score = 0
    iterations = 1
    cleared_quicker_count = 0
    cleared_quicker_value = 0
    default_cleared_quicker_count = 0
    default_cleared_quicker_value = 0
    cleared_and_default_failed_count = 0
    cleared_and_default_failed_value = 0
    failed_and_default_cleared_count = 0
    failed_and_default_cleared_value = 0
    congested_quicker_count = 0
    congested_quicker_value = 0
    default_congested_quicker_count = 0
    default_congested_quicker_value = 0


    for i in range(iterations):
        initial_vehicles = create_random_initial_vehicle_list()
        initial_times = find_new_timings(initial_vehicles)

        outputs = compare_clearance_times(initial_times, initial_vehicles)
        for output in outputs:
            our_score += outputs[output][0]
            cleared, default_cleared, time = outputs[output][1], outputs[output][2], outputs[output][3]
            if cleared and default_cleared:
                if outputs[output][0] == True:
                    cleared_quicker_count += 1
                    cleared_quicker_value += time
                else:
                    default_cleared_quicker_count += 1
                    default_cleared_quicker_value += time
            elif cleared:
                cleared_and_default_failed_count += 1
                cleared_and_default_failed_value += time
            elif default_cleared:
                failed_and_default_cleared_count += 1
                failed_and_default_cleared_value += time
            else:
                if default_cleared > cleared:
                    congested_quicker_count += 1
                    congested_quicker_value += time
                else:
                    default_congested_quicker_count += 1
                    default_congested_quicker_value += time
    plot(
        our_score, iterations * len(default_timings), 
        cleared_quicker_count, cleared_quicker_value,
        default_cleared_quicker_count, default_cleared_quicker_value,
        cleared_and_default_failed_count, cleared_and_default_failed_value,
        failed_and_default_cleared_count, failed_and_default_cleared_value,
        congested_quicker_count, congested_quicker_value,
        default_congested_quicker_count, default_congested_quicker_value
    )
    analyse_and_store(
        our_score, iterations * len(default_timings), 
        cleared_quicker_count, cleared_quicker_value,
        default_cleared_quicker_count, default_cleared_quicker_value,
        cleared_and_default_failed_count, cleared_and_default_failed_value,
        failed_and_default_cleared_count, failed_and_default_cleared_value,
        congested_quicker_count, congested_quicker_value,
        default_congested_quicker_count, default_congested_quicker_value
    )
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("==================================================")
    print(f"Our method is better in {our_score} out of {iterations * len(default_timings)} test cases")
    print("==================================================")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    main()