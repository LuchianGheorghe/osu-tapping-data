import os, statistics, math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def print_t(input):
	print(type(input))
        

def get_data_path():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, 'data')


def get_maps_path():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, 'beatmaps')


def create_empty_series(columns):
    """
    Create an empty Series with the given columns as index.
    """
    return pd.Series(data=[None]*len(columns), index=columns)


def round_divisor(value):
    if value == math.inf:
        return 1
    if value == round(value):
        return value
    thresholds = [0, 12.5, 25, 33, 50, 66, 75, 87.5, 100]
    digits = (value * 100) % 100
    output = 0.0
    for i in range(9):
        if digits <= thresholds[i]:
            halfway = (thresholds[i-1] + thresholds[i]) / 2
            if digits == halfway:
                output = math.floor(value) + halfway / 100
            elif digits < halfway:
                output = math.floor(value) + thresholds[i-1] / 100
            else:
                output = math.floor(value) + thresholds[i] / 100
            break
    return output


def cv_positions(lst, value):
    positions = [i for i, x in enumerate(lst) if x == value]
    if len(positions) <= 1:
        return 0.0
    mean = statistics.mean(positions)
    stdev = statistics.stdev(positions, mean)
    #print(stdev / mean, len(positions), (stdev / mean) * len(positions), value)
    return mean, stdev, stdev / mean, len(positions)


def list_details(lst, value=None):
    positions = [i for i, x in enumerate(lst) if x == value]
    # if 0 not in positions:
    #     positions = [0] + positions
    # if (len(lst) - 1) not in positions:
    #     positions.append(len(lst) - 1)

    if len(positions) <= 1:
        return 0.0
    mean = statistics.mean(positions)
    stdev = statistics.stdev(positions, mean)
    print('list: ', positions)
    print('mean: ', mean)
    print('stdev: ', stdev)
    print('cv: ', stdev / mean)
    print('len(list): ', len(positions))


def parse_list(lst):
    divs = list(set(lst))
    div_info = {}
    for div in divs:
        div_info[div] = cv_positions(lst, div)
        break
    # for div, info in div_info.items():
    #     if info != 0:
    #         print(div, info)


def validate_map_id(map_id):
    return int(map_id)


def get_map_ids_from_file(path):
    with open(path) as file:
        return list(set([validate_map_id(map_id[:-1]) for map_id in file.readlines()]))
