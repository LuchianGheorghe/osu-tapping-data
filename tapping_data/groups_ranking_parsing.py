from tapping_data.helpers import get_parsed_maps_path, get_lists_path, get_parsed_lists_path, round_divisor, create_empty_series, get_map_ids_from_file_path
from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df, visualize_all_groups

import os
import pandas as pd


def compute_times_between_n(map_id: int, between_divisor: float, object_count_n: int) -> list[float]:
    groups_df = get_groups_df(map_id)

    groups_selected = groups_df.loc[
        (groups_df['between_divisor'] == between_divisor) &
        (groups_df['object_count_n'] == object_count_n)
    ].copy()

    if groups_selected.empty:
        raise ValueError(f'Beatmap does not contain any ({between_divisor=}, {object_count_n=}) groups.')

    start_times = groups_selected['start_time'].values
    end_times = groups_selected['end_time'].values

    times_between_n = []
    times_between_n.append(round_divisor(start_times[0] / groups_selected.iloc[0]['beat_length']))

    for i in range(1, len(start_times)):
        difference = start_times[i] - end_times[i - 1]
        beat_length = groups_selected.iloc[i]['beat_length']
        times_between_n.append(round_divisor(difference / beat_length))

    return times_between_n


def compute_freq_times_between_n(times_between_n: list[float]) -> dict[str: float]:
    freq_times_between_n = {'1': 0, '2': 0, '4': 0, '8': 0, '16': 0}

    for time in times_between_n:
        if time < 1:
            freq_times_between_n['1'] += 1
        elif time < 2:
            freq_times_between_n['2'] += 1
        elif time < 4:
            freq_times_between_n['4'] += 1
        elif time < 8:
            freq_times_between_n['8'] += 1
        else:
            freq_times_between_n['16'] += 1

    for freq in freq_times_between_n:
        freq_times_between_n[freq] = round(freq_times_between_n[freq] / len(times_between_n), 2)

    return freq_times_between_n


def compute_indexed_freq_times_between_n(sorted_freq_times_between_n: dict[str: float], threshold: float = 0.1) -> dict[str: float]:
    """
        Given a sorted_freq_times_between_n, 
            {'1': 0.5, '2': 0.2, '4': 0.15, '8': 0}

        Returns a dictionary with the same keys, but the values represent the indexing of the key:
            - usually keys get the index of their position
            - successive keys within 0.1 of each other get the average of their indexes
            - keys associated with values of 0 get the length of the list - 1 as their index 
    """

    ranking_freq_times_between_n = {}

    keys = list(sorted_freq_times_between_n.keys())
    percentages = list(sorted_freq_times_between_n.values())

    sequence_start = 0
    for i in range(len(percentages)):
        if i >= sequence_start:
            sequence_start = i
            current_sequence = set()
            current_sequence.add(sequence_start)
            for j in range(i + 1, len(percentages)):
                if abs(percentages[i] - percentages[j]) <= threshold:
                    current_sequence.add(j)
                    sequence_start = j + 1
                else:
                    sequence_start = j
                    break

            # print(f'{current_sequence=}, {sequence_start=}')
            
            if len(current_sequence) > 1: 
                mean = sum(list(current_sequence)) / len(current_sequence)
                for idx in current_sequence:
                    ranking_freq_times_between_n[keys[idx]] = mean
            else:
                idx = list(current_sequence)[0]
                ranking_freq_times_between_n[keys[idx]] = int(idx)

    for key, val in sorted_freq_times_between_n.items():
        if val == 0:
            ranking_freq_times_between_n[key] = len(percentages) - 1

    return ranking_freq_times_between_n


def compute_inversed_indexed_freq_times_between_n(indexed_freq_times_between_n: dict[str: float]) -> dict[str: float]:
    inverse_indexed_freq_times_between_n = {}
    
    length = len(indexed_freq_times_between_n)
    for key, value in indexed_freq_times_between_n.items():
        # inverse_indexed_freq_times_between_n[key] = pow(2, len(indexed_freq_times_between_n) - value)
        inverse_indexed_freq_times_between_n[key] = length - value - 1
    
    return inverse_indexed_freq_times_between_n


def compute_scaled_inversed_indexed_freq_times_between_n(inverse_indexed_freq_times_between_n: dict[str: float]) -> dict[str: float]:
    scaled_inversed_indexed_freq_times_between_n = {}
    
    length = len(inverse_indexed_freq_times_between_n)
    for key, value in inverse_indexed_freq_times_between_n.items():
        scaling_factor = (pow(2, length - 1) / int(key)) + 1
        scaled_inversed_indexed_freq_times_between_n[key] = scaling_factor * value
    
    return scaled_inversed_indexed_freq_times_between_n


def compute_normalized_inversed_indexed_freq_times_between_n(inverse_indexed_freq_times_between_n: dict[str: float], sorted_freq_times_between_n: dict[str: float]) -> dict[str: float]:
    normalized_inverse_indexed_freq_times_between_n = {}
    
    for key, value in inverse_indexed_freq_times_between_n.items():
        normalized_inverse_indexed_freq_times_between_n[key] = round(sorted_freq_times_between_n[key] * value, 2)
    
    return normalized_inverse_indexed_freq_times_between_n


def map_id_to_ranking(map_id: float, between_divisor: float, object_count_n: int, debug: bool = False) -> list[float]:
    times_between_n = compute_times_between_n(map_id, between_divisor, object_count_n)
    freq_times_between_n = compute_freq_times_between_n(times_between_n)
    sorted_freq_times_between_n = dict(sorted(freq_times_between_n.items(), key=lambda item: item[1], reverse=True))
    indexed_freq_times_between_n = compute_indexed_freq_times_between_n(sorted_freq_times_between_n)
    inversed_indexed_freq_times_between_n = compute_inversed_indexed_freq_times_between_n(indexed_freq_times_between_n)
    scaled_inversed_indexed_freq_times_between_n = compute_scaled_inversed_indexed_freq_times_between_n(inversed_indexed_freq_times_between_n)
    normalized_inverse_indexed_freq_times_between_n = compute_normalized_inversed_indexed_freq_times_between_n(scaled_inversed_indexed_freq_times_between_n, sorted_freq_times_between_n)

    if debug:
        print(map_id)
        print(f'{sorted_freq_times_between_n = }')
        print(f'{indexed_freq_times_between_n = }')
        print(f'{inversed_indexed_freq_times_between_n = }')
        print(f'{scaled_inversed_indexed_freq_times_between_n = }')
        print(f'{normalized_inverse_indexed_freq_times_between_n = }')
        print()

    return normalized_inverse_indexed_freq_times_between_n


def selected_group_count(map_id: int, between_divisor: float, object_count_n: int) -> int:
    groups_df = get_groups_df(map_id)

    return len(groups_df.loc[
        (groups_df['between_divisor'] == between_divisor) &
        (groups_df['object_count_n'] == object_count_n)
    ])


def selected_group_bpm(map_id: int, between_divisor: float, object_count_n: int) -> int:
    groups_df = get_groups_df(map_id)

    return 60000 / groups_df.loc[
        (groups_df['between_divisor'] == between_divisor) &
        (groups_df['object_count_n'] == object_count_n)
    ]['beat_length'].mean()


def cast_types_groups_ranking(groups_ranking_df: pd.DataFrame) -> pd.DataFrame:
    groups_ranking_df['map_id'] = groups_ranking_df['map_id'].astype('int32')
    groups_ranking_df['group_type'] = groups_ranking_df['group_type'].astype('object')
    groups_ranking_df['ranking'] = groups_ranking_df['ranking'].astype('object')
    groups_ranking_df['group_count'] = groups_ranking_df['group_count'].astype('int32')
    groups_ranking_df['bpm'] = groups_ranking_df['bpm'].astype('float16')
    return groups_ranking_df


def parse_groups_ranking(map_id: int, between_divisor: float, object_count_n: int, map_groups_ranking_file: str) -> None:
    columns = ['map_id', 'group_type', 'ranking', 'group_count', 'bpm']
    groups_ranking_df = pd.DataFrame(columns=columns)

    ranking = map_id_to_ranking(map_id, between_divisor=between_divisor, object_count_n=object_count_n)
    new_row = create_empty_series(columns=columns)

    new_row['map_id'] = map_id
    new_row['group_type'] = f'divisor_{between_divisor}_count_{object_count_n}'
    new_row['ranking'] = ranking
    new_row['group_count'] = selected_group_count(map_id, between_divisor, object_count_n)
    new_row['bpm'] = selected_group_bpm(map_id, between_divisor, object_count_n)

    groups_ranking_df = pd.concat([groups_ranking_df, new_row.to_frame().T], ignore_index=True)
    groups_ranking_df = cast_types_groups_ranking(groups_ranking_df)

    groups_ranking_df.to_parquet(map_groups_ranking_file, index=False)


def get_groups_ranking_df(map_id: int, between_divisor: float, object_count_n: int, update_entry : bool = False) -> pd.DataFrame:
    map_groups_ranking_file = os.path.join(get_parsed_maps_path(), str(map_id) + f'_divisor_{between_divisor}_count_{object_count_n}_ranking.parquet')

    if not os.path.exists(map_groups_ranking_file) or update_entry:
        parse_groups_ranking(map_id, between_divisor, object_count_n, map_groups_ranking_file)

    return pd.read_parquet(map_groups_ranking_file)


def cast_types_groups_rankings_list(groups_rankings_list_df: pd.DataFrame) -> pd.DataFrame:
    groups_rankings_list_df['map_id'] = groups_rankings_list_df['map_id'].astype('int32')
    groups_rankings_list_df['group_type'] = groups_rankings_list_df['group_type'].astype('object')
    groups_rankings_list_df['ranking'] = groups_rankings_list_df['ranking'].astype('object')
    groups_rankings_list_df['group_count'] = groups_rankings_list_df['group_count'].astype('int32')
    groups_rankings_list_df['bpm'] = groups_rankings_list_df['bpm'].astype('float16')
    groups_rankings_list_df['distance'] = groups_rankings_list_df['distance'].astype('float16')
    return groups_rankings_list_df


def parse_groups_rankings_list(map_list_file: str, between_divisor: float, object_count_n: int, map_groups_rankings_list_file: str, update_entry: bool = False) -> None:
    map_list_file_path = os.path.join(get_lists_path(), map_list_file)
    map_ids = get_map_ids_from_file_path(map_list_file_path)

    columns = ['map_id', 'group_type', 'ranking', 'group_count', 'bpm', 'distance']
    groups_rankings_list_df = pd.DataFrame(columns=columns)
    
    len_map_ids = len(map_ids)
    progress = 1

    for map_id in map_ids:
        try:
            print(f'Progress: {progress}/{len_map_ids}: {map_id}')
            groups_ranking_df = get_groups_ranking_df(map_id, between_divisor, object_count_n, update_entry)
            groups_rankings_list_df = pd.concat([groups_rankings_list_df, groups_ranking_df], ignore_index=True)
        except Exception as e:
            print(map_id, e)
        
        progress += 1
        
    groups_rankings_list_df['distance'] = 0
    groups_rankings_list_df = cast_types_groups_rankings_list(groups_rankings_list_df)
    
    groups_rankings_list_df.to_parquet(map_groups_rankings_list_file, index=False)


def get_groups_rankings_list_df(map_list_file: str, between_divisor: float, object_count_n: int, update_entry : bool = False) -> pd.DataFrame:
    map_list_file_name, _ = os.path.splitext(map_list_file)
    map_groups_rankings_list_file = os.path.join(get_parsed_lists_path(), str(map_list_file_name) + f'_divisor_{between_divisor}_count_{object_count_n}_rankings.parquet')
    
    if not os.path.exists(map_groups_rankings_list_file) or update_entry:
        parse_groups_rankings_list(map_list_file, between_divisor, object_count_n, map_groups_rankings_list_file, update_entry)
    
    return pd.read_parquet(map_groups_rankings_list_file)