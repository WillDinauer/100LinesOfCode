"""
seed_puzzle.py

Solution of seed puzzle and visualization of transitions in 100 Lines of Code.

William Dinauer, 2023
"""
import time
import matplotlib.pyplot as plt
import numpy as np

def plot_seed_history(seed_history, transition_history, seed_color_history, filename):
    plt.figure(figsize=(15, 15))
    for iteration, (seeds, colors) in enumerate(zip(seed_history, seed_color_history)): # Plot ranges
        for pair, color in zip(seeds, colors):
            plt.barh(iteration, pair[1] - pair[0] + 1, left=pair[0], color=color, height=0.5, alpha=0.7)

    for iteration, (transitions, colors) in enumerate(zip(transition_history, seed_color_history[1:])):
        for pair, color in zip(transitions, colors):                        # Plot transitions between ranges
            start_pair, end_pair = pair[0], pair[1]
            x_values_start = np.linspace(start_pair[0], start_pair[1], 50)  # Generate intermediate points for a smoother transition
            x_values_end = np.linspace(end_pair[0], end_pair[1], 50)
            x_values = np.vstack([x_values_start, x_values_end])            # Prepare data for vectorized plotting
            y_values = np.vstack([np.full(50, iteration), np.full(50, iteration + 1)])
            plt.plot(x_values, y_values, color=color, alpha=0.3)            # Plot the lines in a vectorized manner
    plt.title('Evolution of Seeds Through Transitions')
    plt.xlabel('Seed Value')
    plt.ylabel('Iteration')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Transition graphic saved to {filename}")

def intersection(a, b):                             # Returns the intersection between two [start, end] pairs
    left, right = max(a[0], b[0]), min(a[1], b[1])
    return [left, right] if right >= left else []

def update_unmapped(unmapped_seeds, seedlet):
    new_unmapped_seeds = []
    for pair in unmapped_seeds:                                 # For all previously unmapped seeds, determine if it was just mapped to a new value
        intersect = intersection(seedlet, pair)
        if intersect == []:                                     # No intersection -- this pair remains unmapped
            new_unmapped_seeds.append(pair)
        elif seedlet[0] > pair[0]:                              # Seeds less than the start of the range remain unmapped
            new_unmapped_seeds.append([pair[0], seedlet[0]-1])
        elif seedlet[1] < pair[1]:                              # Seeds greater than the end of the range remain unmapped
            new_unmapped_seeds.append([seedlet[1]+1, pair[1]])
    return new_unmapped_seeds

def map_seeds(seeds, grid, seed_colors):
    new_seeds, transitions, new_seed_colors = [], [], []
    for idx, pair in enumerate(seeds):  # Map every existing range of seeds into a new set of ranges
        unmapped = [pair.copy()]        # 'unmapped' begins as the original range of seeds, but grows to contain ranges of all unmapped seeds
        for r in range(len(grid)):      # Check for an intersection between the range of seeds and entries in the map
            seedlet = intersection(pair, [grid[r][1], grid[r][1] + grid[r][2] - 1])
            if seedlet != []:           # Intersection found
                unmapped = update_unmapped(unmapped, seedlet)
                mapped_range = [grid[r][0] + (seedlet[0]-grid[r][1]), grid[r][0] + (seedlet[1]-grid[r][1])]  # Mapping function for the new range of seeds
                new_seeds.append(mapped_range)
                transitions.append([pair, mapped_range])
                new_seed_colors.append(seed_colors[idx])
        for pair in unmapped:           # Unmapped seeds map 1-to-1 (new_value = old_value)
            new_seeds.append(pair)
            transitions.append([pair, pair])
            new_seed_colors.append(seed_colors[idx])
    return new_seeds, transitions, new_seed_colors

def transition(seeds, f, seed_colors):
    while True:                    # Read from the file until we reach the beginning of the map's actual values
        line = f.readline().strip()
        if "map" in line:
            line = f.readline().strip()
            break
    grid = []                      # Read the values of the map into rows of [new_value_start, old_value_start, range]
    while line != "":
        grid.append([int(x) for x in line.split()])
        line = f.readline().strip()
    return map_seeds(seeds, grid, seed_colors)  # Return the newly mapped seeds

def solve_puzzle(filename):
    try: 
        with open(filename, "r") as f:
            seed_colors = ['red', 'green', 'blue', 'orange', 'purple', 'brown', 'pink', 'gray', 'black', 'cyan']    # Assign each seed range a color
            nums = [int(x) for x in f.readline().strip("seeds: ").strip().split(" ")]       # Read the first line as an array of numbers
            seeds = [[nums[i], nums[i] + nums[i+1] - 1] for i in range(0, len(nums), 2)]    # Array of [start, end] pairs. Each element represents a range of values
            seed_history, transition_history, seed_color_history = [seeds], [], [seed_colors]
            for i in range(7):  # Constant number of maps (7)
                seeds, transitions, seed_colors = transition(seeds, f, seed_colors)      # Map the seeds to their new value
                seed_history.append(seeds)
                transition_history.append(transitions)
                seed_color_history.append(seed_colors)
        return min(seeds[0:])[0], seed_history, transition_history, seed_color_history   # Return minimum seed value and plotting params
    except FileNotFoundError:
        print(f"File {filename} not found.")

if __name__ == '__main__':
    start_time = time.time()
    res, seed_history, transition_history, seed_color_history = solve_puzzle("input.txt")
    end_time = time.time()
    print(f"Solved puzzle in {end_time-start_time:.5f} seconds with solution {res}")
    plot_seed_history(seed_history, transition_history, seed_color_history, "mapping.png")