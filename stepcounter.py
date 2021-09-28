import numpy as np
import matplotlib.pyplot as plt

INTERVAL = 34
DYNAMIC_THRESHOLDS = []
COUNT = 0

# Simple function to visualize 4 arrays that are given to it
def visualize_data(timestamps, x_arr, y_arr, z_arr, s_arr):
    # Plotting accelerometer readings
    plt.figure(1)
    plt.plot(timestamps, x_arr, color="blue", linewidth=1.0)
    plt.plot(timestamps, y_arr, color="red", linewidth=1.0)
    plt.plot(timestamps, z_arr, color="green", linewidth=1.0)
    plt.show()
    # magnitude array calculation
    m_arr = []
    for i, x in enumerate(x_arr):
        m_arr.append(magnitude(x_arr[i], y_arr[i], z_arr[i]))
    plt.figure(2)
    # plotting magnitude and steps
    marks = [n > 0 for n in s_arr]
    plt.plot(timestamps, m_arr, '-gD', markevery=marks, linewidth=1.0)

    if len(DYNAMIC_THRESHOLDS) == 1:
        plt.axhline(y=get_threshold(m_arr), color='black', linestyle='-')
    else:
        for i, threshold in enumerate(DYNAMIC_THRESHOLDS):
            if (i * INTERVAL) + INTERVAL >= len(timestamps):
                plt.plot([i * INTERVAL, len(timestamps) - 1], [threshold, threshold], color='black')
            else:
                plt.plot([i * INTERVAL, (i * INTERVAL) + INTERVAL], [threshold, threshold], color='black')

    print("Rec count: " + str(COUNT))
    DYNAMIC_THRESHOLDS.clear()
    plt.show()


# Function to read the data from the log file
# TODO Read the measurements into array variables and return them
def read_data(filename):
    timestamps = list()
    x_arr = list()
    y_arr = list()
    z_arr = list()
    for row in np.genfromtxt(filename, delimiter=','):
        timestamps.append(row[0])
        x_arr.append(row[1])
        y_arr.append(row[2])
        z_arr.append(row[3])

    return timestamps, x_arr, y_arr, z_arr


# Function to count steps.
# Should return an array of timestamps from when steps were detected
# Each value in this array should represent the time that step was made.
def count_steps(timestamps, x_arr, y_arr, z_arr):
    rv = []
    magnitudes = [magnitude(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(timestamps))]
    threshold = get_threshold(magnitudes)
    DYNAMIC_THRESHOLDS.append(threshold) # For visualization
    for i, time in enumerate(timestamps):
        if i > 0 and magnitudes[i] >= threshold > magnitudes[i - 1]:
            rv.append(time)

    return rv


def rec_count_steps(timestamps, x_arr, y_arr, z_arr, interval, n):
    if n >= len(timestamps) - 1:
        return []
    COUNT = COUNT + 1
    if n + interval >= len(timestamps):
        interval = len(timestamps) - 1

    return count_steps(timestamps[n:n+interval], x_arr[n:n+interval], y_arr[n:n+interval], z_arr[n:n+interval]) +\
        rec_count_steps(timestamps, x_arr, y_arr, z_arr, interval, n + interval)


def dynamic_count_steps(timestamps, x_arr, y_arr, z_arr, interval):
    return rec_count_steps(timestamps, x_arr, y_arr, z_arr, interval, 0)


def get_threshold(magnitudes):
    return (min(magnitudes) + max(magnitudes)) / 2


# Calculate the magnitude of the given vector
def magnitude(x, y, z):
    return np.linalg.norm((x, y, z))


# Function to convert array of times where steps happened into array to give into graph visualization
# Takes timestamp-array and array of times that step was detected as an input
# Returns an array where each entry is either zero if corresponding timestamp has no step detected or 50000 if
# the step was detected
def generate_step_array(timestamps, step_time):
    s_arr = []
    ctr = 0
    for i, time in enumerate(timestamps):
        if ctr < len(step_time) and step_time[ctr] <= time:
            ctr += 1
            s_arr.append(50000)
        else:
            s_arr.append(0)
    while len(s_arr) < len(timestamps):
        s_arr.append(0)
    return s_arr


# Check that the sizes of arrays match
def check_data(t, x, y, z):
    if len(t) != len(x) or len(y) != len(z) or len(x) != len(y):
        print("Arrays of incorrect length")
        return False
    print("The amount of data read from accelerometer is " + str(len(t)) + " entries")
    return True


def main():
    # read data from a measurement file, change the inoput file name if needed
    timestamps, x_array, y_array, z_array = read_data("data/fastwalking.csv")
    # Chek that the data does not produce errors
    if not check_data(timestamps, x_array, y_array, z_array):
        return
    # Count the steps based on array of measurements from accelerometer
    #st = count_steps(timestamps, x_array, y_array, z_array)
    st = dynamic_count_steps(timestamps, x_array, y_array, z_array, INTERVAL)
    # Print the result
    print("This data contains " + str(len(st)) + " steps according to current algorithm")
    # convert array of step times into graph-compatible format
    s_array = generate_step_array(timestamps, st)
    # visualize data and steps
    visualize_data(timestamps, x_array, y_array, z_array, s_array)


main()
