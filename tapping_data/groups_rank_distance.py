from tapping_data.context_sections_parsing import get_all_context_sections_stats_dict
from tapping_data.sections_statistics import get_sections_stats_dict
from tapping_data.sections_parsing import get_sections_dfs_dict, visualize_sections
from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df
from tapping_data.groups_embedding_attempts import create_model, get_similar_maps_doc2vec, map_id_to_document_context_sections, map_ids_to_sequences_df, sgt_search, map_ids_to_section_sequences_df, map_id_to_document_all_groups
from tapping_data.helpers import get_map_ids_from_file_path, get_lists_path, create_empty_series, round_divisor, get_parsed_lists_path
from tapping_data.map_list_sections_stats_parsing import get_map_list_sections_stats_df
from tapping_data.map_list_sections_stats_similarity import get_similar_maps, target_section_clustering

from beatmap_reader import BeatmapIO

import matplotlib.pyplot as plt
import pandas as pd

import webbrowser
import time
import os
import pickle


def compute_times_between_n(map_id: int, between_divisor: float, object_count_n: int, debug_mode: bool = False) -> list[float]:
    """
    
    """

    groups_df = get_groups_df(map_id)
    #visualize_sections(groups_df)
    #plt.show()

    groups_selected = groups_df.loc[
        (groups_df['between_divisor'] == between_divisor) &
        (groups_df['object_count_n'] == object_count_n)
    ].copy()

    if groups_selected.empty:
        raise ValueError(f'Beatmap does not contain any ({between_divisor=}, {object_count_n=}) groups.')

    start_times = groups_selected['start_time'].values
    end_times = groups_selected['end_time'].values

    times_between = []
    times_between_n = []

    for i in range(1, len(start_times)):
        difference = start_times[i] - end_times[i - 1]
        beat_length = groups_selected.iloc[i]['beat_length']
        times_between.append(difference)
        times_between_n.append(round_divisor(difference / beat_length))
    
    if debug_mode:
        print(map_id, times_between)
        print(map_id, times_between_n)
        print()

        plt.plot(start_times)
        plt.plot(times_between)
        plt.show()

    return times_between_n


def compute_freq_times_between_n(times_between_n: list[float]) -> dict[str: float]:
    """

    """

    freq_times_between_n = {'2': 0, '4': 0, '8': 0, '16': 0, '32': 0}

    for time in times_between_n:
        if time < 2:
            freq_times_between_n['2'] += 1
        elif time < 4:
            freq_times_between_n['4'] += 1
        elif time < 8:
            freq_times_between_n['8'] += 1
        elif time < 16:
            freq_times_between_n['16'] += 1
        else:
            freq_times_between_n['32'] += 1
                
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
            - keys associated with values of 0 get the length of the list as their index 
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
                else:
                    sequence_start = j
                    break
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


def map_id_to_ranking(map_id: float, between_divisor: float, object_count_n: int, debug_mode: bool = False) -> list[float]:
    """

    """

    times_between_n = compute_times_between_n(map_id, between_divisor=4.0, object_count_n=16, debug_mode=debug_mode)
    freq_times_between_n = compute_freq_times_between_n(times_between_n)
    sorted_freq_times_between_n = dict(sorted(freq_times_between_n.items(), key=lambda item: item[1], reverse=True))
    indexed_freq_times_between_n = compute_indexed_freq_times_between_n(sorted_freq_times_between_n)

    # print(map_id, sorted_freq_times_between_n, indexed_freq_times_between_n, list(indexed_freq_times_between_n), list(indexed_freq_times_between_n.values()))

    return indexed_freq_times_between_n


def compute_rank_distance(indexed_ranking_a, indexed_ranking_b, series: bool = True) -> int:
    """

    """

    distance = sum(abs(indexed_ranking_a[item] - indexed_ranking_b[item]) for item in indexed_ranking_a)

    return distance


def compute_rank_distance_against_series(indexed_ranking_a: dict, series_rankings: pd.Series) -> int:
    """

    """

    distances = []
    for ranking in series_rankings:
        distance = sum(abs(indexed_ranking_a[item] - ranking[item]) for item in indexed_ranking_a)
        distances.append(distance)

    return pd.Series(distances)


def selected_group_count(map_id: int, between_divisor: float, object_count_n: int) -> int:
    """
    
    """

    groups_df = get_groups_df(map_id)

    return len(groups_df.loc[
        (groups_df['between_divisor'] == between_divisor) &
        (groups_df['object_count_n'] == object_count_n)
    ])


def get_similar_maps_by_rank_distance(target_map_id: str, target_between_divisor: float, target_object_count_n: float, top_n: int, map_list_file: str, visualize: bool = False, open_links: bool = False) -> None:
    """
    
    """
    
    file_name, _ = os.path.splitext(map_list_file)
    rank_distance_file = file_name + f'_divisor_{target_between_divisor}_count_{target_object_count_n}_rank_distance.parquet'
    rank_distance_file_path = os.path.join(get_parsed_lists_path(), rank_distance_file)

    if not os.path.exists(rank_distance_file_path):
        map_list_file_path = os.path.join(get_lists_path(), map_list_file)
        map_ids = get_map_ids_from_file_path(map_list_file_path)

        columns = ['map_id', 'group_count', 'ranking', 'rank_distance']
        rankings_df = pd.DataFrame(columns=columns)
        
        for map_id in map_ids:
            try:
                ranking = map_id_to_ranking(map_id, between_divisor=target_between_divisor, object_count_n=target_object_count_n)

                new_row = create_empty_series(columns=columns)
                new_row['map_id'] = map_id
                # new_row['group_type'] = f'divisor_{target_between_divisor}_count_{target_object_count_n}'
                new_row['group_count'] = selected_group_count(map_id, target_between_divisor, target_object_count_n)
                new_row['ranking'] = ranking
                new_row['rank_distance'] = 0

                rankings_df = pd.concat([rankings_df, new_row.to_frame().T], ignore_index=True)
            except Exception as e:
                print(map_id, e)

        rankings_df['map_id'] = rankings_df['map_id'].astype('int32')
        # rankings_df['group_type'] = rankings_df['group_type'].astype('string')
        rankings_df['group_count'] = rankings_df['group_count'].astype('int32')
        rankings_df['ranking'] = rankings_df['ranking'].astype('object')
        rankings_df['rank_distance'] = rankings_df['rank_distance'].astype('int32')

        rankings_df.to_parquet(rank_distance_file_path, index=False)
    else:
        rankings_df = pd.read_parquet(rank_distance_file_path)

    target_ranking = map_id_to_ranking(target_map_id, between_divisor=target_between_divisor, object_count_n=target_object_count_n)
    rankings_df['rank_distance'] = compute_rank_distance_against_series(target_ranking, rankings_df['ranking'])

    target_group_count = selected_group_count(target_map_id, target_between_divisor, target_object_count_n)
    group_count_filter = abs(rankings_df['group_count'] - target_group_count) < target_group_count * 0.50

    rankings_df = rankings_df.loc[group_count_filter].sort_values('rank_distance')

    similarity_search_map_ids = rankings_df['map_id'].values.tolist()[:top_n]

    visualize_sections(get_groups_df(target_map_id))

    if visualize:
        for map_id in similarity_search_map_ids:
            groups_df = get_groups_df(map_id)
            visualize_sections(groups_df)

    if open_links:
        for map_id in similarity_search_map_ids:
            webbrowser.open(f'https://osu.ppy.sh/b/{map_id}')
            time.sleep(0.5)

    plt.show()