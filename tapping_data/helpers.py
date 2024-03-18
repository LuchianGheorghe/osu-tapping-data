import os, math
import pandas as pd


def print_t(input):
	print(type(input))
        

def get_downloaded_maps_path():
    dirname = os.path.dirname(__file__)
    maps_path = os.path.join(dirname, '..', 'content', 'beatmaps')
    if not os.path.exists(maps_path):
        os.makedirs(maps_path)
    return maps_path


def get_parsed_maps_path():
    dirname = os.path.dirname(__file__)
    parsed_maps_path = os.path.join(dirname, '..', 'content', 'beatmaps_parsed')
    if not os.path.exists(parsed_maps_path):
        os.makedirs(parsed_maps_path)
    return parsed_maps_path


def get_lists_path():
    dirname = os.path.dirname(__file__)
    map_lists_path = os.path.join(dirname, '..', 'content', 'lists')
    if not os.path.exists(map_lists_path):
        os.makedirs(map_lists_path)
    return map_lists_path


def get_parsed_lists_path():
    dirname = os.path.dirname(__file__)
    parsed_map_lists_path = os.path.join(dirname, '..', 'content', 'lists_parsed')
    if not os.path.exists(parsed_map_lists_path):
        os.makedirs(parsed_map_lists_path)
    return parsed_map_lists_path


def create_empty_series(columns, content=None):
    return pd.Series(data=[content]*len(columns), index=columns)


def round_divisor(value):
    if value == math.inf:
        return 1
    if value == round(value):
        return value
    thresholds = [0, 25, 33, 50, 66, 75, 100]
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


def validate_map_id(map_id):
    return int(map_id)


def get_map_ids_from_file_path(path):
    with open(path) as file:
        return list(set([validate_map_id(map_id[:-1]) for map_id in file.readlines()]))
