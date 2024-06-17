from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df, visualize_all_groups
from tapping_data.groups_ranking_parsing import get_groups_rankings_list_df, map_id_to_ranking, selected_group_count
from tapping_data.helpers import get_map_ids_from_file_path, get_lists_path, create_empty_series, round_divisor, get_parsed_lists_path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import webbrowser
import time
import os


def compute_rank_distance(indexed_ranking_a: dict, indexed_ranking_b: dict) -> int:
    distance = sum(abs(indexed_ranking_a[item] - indexed_ranking_b[item]) for item in indexed_ranking_a)
    return distance


def compute_rank_distance_against_series(indexed_ranking_a: dict, series_rankings: pd.Series) -> int:
    distances = []
    for ranking in series_rankings:
        distance = sum(abs(indexed_ranking_a[item] - ranking[item]) for item in indexed_ranking_a)
        distances.append(distance)
    
    return pd.Series(distances)


def compute_total_rank_distance(indexed_ranking_a: dict, indexed_ranking_b: dict, series: bool = True) -> int:
    for i in range(1, len(indexed_ranking_a)):
        for key, value in indexed_ranking_a.items():
            if value <= i:
                pass


def get_distance_matrix(groups_rankings_list_df: pd.DataFrame, distance = compute_rank_distance) -> np.ndarray:
    n_samples = groups_rankings_list_df.shape[0]

    distance_matrix = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            ranking_i = groups_rankings_list_df.iloc[i]['ranking']
            ranking_j = groups_rankings_list_df.iloc[j]['ranking']
            distance_matrix[i, j] = distance_matrix[j, i] = distance(ranking_i, ranking_j)

    return distance_matrix


def get_similar_maps_by_rank_distance(map_list_file: str, target_map_id: str, target_between_divisor: float, target_object_count_n: float, top_n: int, visualize: bool = False, open_links: bool = False) -> None:
    groups_rankings_list_df = get_groups_rankings_list_df(map_list_file, target_between_divisor, target_object_count_n)

    target_ranking = map_id_to_ranking(target_map_id, target_between_divisor, target_object_count_n)
    groups_rankings_list_df['distance'] = compute_rank_distance_against_series(target_ranking, groups_rankings_list_df['ranking'])

    target_group_count = selected_group_count(target_map_id, target_between_divisor, target_object_count_n)
    group_count_filter = abs(groups_rankings_list_df['group_count'] - target_group_count) > target_group_count * 0.50

    groups_rankings_list_df = groups_rankings_list_df.loc[group_count_filter].sort_values('distance')

    similarity_search_map_ids = groups_rankings_list_df['map_id'].values.tolist()[:top_n]

    visualize_all_groups(target_map_id)

    print(groups_rankings_list_df.head(50).to_string())

    if visualize:
        for map_id in similarity_search_map_ids:
            visualize_all_groups(map_id)

    if open_links:
        for map_id in similarity_search_map_ids:
            webbrowser.open(f'https://osu.ppy.sh/b/{map_id}')
            time.sleep(0.5)

    plt.show()

    return 