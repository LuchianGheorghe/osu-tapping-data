from tapping_data.helpers import round_divisor
import pandas as pd
import numpy as np
import jenkspy
import bisect
import math


def get_similar_groups_by_divisor_and_count_n(groups_df: pd.DataFrame) -> dict[str: list[pd.DataFrame]]:
    """
    
    """
    
    groups_df_sorted = groups_df.sort_values(by=['between_divisor', 'object_count_n'], ascending=False).reset_index(drop=True)
    
    similar_groups = {}
    columns = groups_df.columns
    new_similar = pd.DataFrame(columns=columns)

    for i, curr_row in groups_df_sorted.iterrows():
        key = f'divisor_{round_divisor(curr_row.between_divisor)}_count_{int(curr_row.object_count_n)}'
        
        if new_similar.empty:
            new_similar = curr_row.to_frame().T.reset_index(drop=True)

        if i == groups_df_sorted.shape[0] - 1:
            similar_groups[key] = [new_similar]
            break

        next_row = groups_df_sorted.iloc[i+1]
        if next_row['between_divisor'] == curr_row['between_divisor'] and next_row['object_count_n'] == curr_row['object_count_n']:
            new_similar = pd.concat([new_similar, next_row.to_frame().T], ignore_index=True)
        else:
            similar_groups[key] = [new_similar]
            new_similar = pd.DataFrame(columns=columns)

    return similar_groups


def split_list_at_values(sorted_list, split_values):
    """
    
    """
    
    split_indices = [bisect.bisect_right(sorted_list, val) for val in split_values]
    split_indices = [0] + split_indices + [len(sorted_list)]

    return [sorted_list[split_indices[i]:split_indices[i + 1]] for i in range(len(split_indices) - 1) if split_indices[i] != split_indices[i + 1]]


def split_similar_groups_by_variance(start_times: list[float]) -> list[list[float]]:
    """
    
    """

    prev_score = math.inf
    score = 0
    nr_of_splits = 1
    while nr_of_splits <= len(start_times):
        jnb = jenkspy.JenksNaturalBreaks(nr_of_splits)
        jnb.fit(start_times)
        total_variance = 0
        for group in jnb.groups_:
            total_variance += np.var(group, ddof=0) / 1000000
        score = total_variance + nr_of_splits * 500
        
        if score > prev_score: break
        # print(f'total_variance: {total_variance}, nr_of_splits: {nr_of_splits}, score: {score}')

        prev_score = score
        best_fit = jnb
        nr_of_splits += 1
    
    variance_split_groups_start_times = []
    for split_group in best_fit.groups_:
        variance_split_groups_start_times.append(split_group.tolist())
        
    return variance_split_groups_start_times


def split_similar_groups_by_pauses(groups_df: pd.DataFrame, start_times: list[list[float]]) -> list[list[float]]:
    """
    
    """
    
    pause_points = groups_df[groups_df.next_divisor < 1]['start_time'].to_list()

    pause_split_groups_start_times = []
    for split_group in start_times:
        pause_split_group = split_list_at_values(split_group, pause_points)
        pause_split_groups_start_times += pause_split_group

    return pause_split_groups_start_times

    
def get_similar_groups_split_dfs(groups_df: pd.DataFrame, start_times: list[list[float]]):
    """
    
    """
    
    similar_split_group_dfs = []

    for split_group_start_times in start_times:
        split_group_df = groups_df.loc[groups_df['start_time'].isin(split_group_start_times)]
        similar_split_group_dfs.append(split_group_df)

    return similar_split_group_dfs


def split_similar_groups(groups_df: pd.DataFrame, similar_groups: dict[str: list[pd.DataFrame]]) -> dict[str: list[pd.DataFrame]]:
    """
        Todo: instead of using start_times, create a list of the times between the groups and check the variance based on that.
    """

    for key in similar_groups:
        start_times = similar_groups[key][0]['start_time'].to_list()

        if len(start_times) == 1: continue

        split_groups_start_times = split_similar_groups_by_variance(start_times)
        split_groups_start_times = split_similar_groups_by_pauses(groups_df, split_groups_start_times)
        
        similar_groups[key] = get_similar_groups_split_dfs(groups_df, split_groups_start_times)

    return similar_groups


def get_similar_groups_dfs_dict(groups_df: pd.DataFrame) -> dict[str: list[pd.DataFrame]]:
    """
        Divides a groups_df into
    """

    similar_groups = get_similar_groups_by_divisor_and_count_n(groups_df)
    similar_groups = split_similar_groups(groups_df, similar_groups)

    return similar_groups
