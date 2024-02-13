import os, math
import pandas as pd
import matplotlib.pyplot as plt
from map_groups import get_groups_df
from helper import print_t, get_data_path, round_divisor, create_empty_series
import numpy as np
import jenkspy
import bisect
from scipy.linalg import svd
import statistics


def cast_types(clusters_df):
    return clusters_df


def remove_non_consecutive_first_occurrence(nums):
    # List to store the result
    result = []
    
    i = 0
    while i < len(nums) - 1:
        # Check if current number and next number are consecutive
        if nums[i] + 1 == nums[i + 1]:
            # Add current number if not already in result
            if not result or nums[i] != result[-1]:
                result.append(nums[i])
            
            # Skip the rest of the consecutive sequence
            while i < len(nums) - 1 and nums[i] + 1 == nums[i + 1]:
                i += 1
        i += 1
    
    return result


def split_list_at_values(sorted_list, split_values):
    # Find the indices where the list should be split
    split_indices = [bisect.bisect_right(sorted_list, val) for val in split_values]
    
    # Add the start and end indices
    split_indices = [0] + split_indices + [len(sorted_list)]
    
    # Split the list using list slicing, excluding empty lists
    return [sorted_list[split_indices[i]:split_indices[i + 1]] for i in range(len(split_indices) - 1) if split_indices[i] != split_indices[i + 1]]


def get_similar_clusters(groups_df):
    groups_df_sorted = groups_df.sort_values(by=['between_divisor', 'object_count_n'], ascending=False).reset_index(drop=True)
    
    similar_clusters = {}
    new_similar = []
    for i, curr_row in groups_df_sorted.iterrows():
        key = f'divisor_{round_divisor(curr_row.between_divisor)}_count_{int(curr_row.object_count_n)}'
        
        if len(new_similar) == 0: 
            new_similar.append(curr_row)

        if i == groups_df_sorted.shape[0] - 1:
            similar_clusters[key] = new_similar
            break

        next_row = groups_df_sorted.iloc[i+1]
        if next_row['between_divisor'] == curr_row['between_divisor'] and next_row['object_count_n'] == curr_row['object_count_n']:
            new_similar.append(next_row)
        else:
            similar_clusters[key] = new_similar
            new_similar = []

    return similar_clusters


def get_split_similar_clusters(groups_df, similar_clusters):
    for key in similar_clusters:
        split_cluster = []
        start_times = []
        for group in similar_clusters[key]:
            start_times.append(group['start_time'])
        if len(start_times) > 1:
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
            variance_split_clusters_start_times = best_fit.groups_

            pause_split_points = groups_df[groups_df.next_divisor < 1]['start_time'].to_list()
            for variance_split_cluster_start_times in variance_split_clusters_start_times:
                pause_split_clusters_start_times = split_list_at_values(variance_split_cluster_start_times.tolist(), pause_split_points)
                for pause_split_cluster_start_times in pause_split_clusters_start_times:
                    pause_split_cluster_rows_df = groups_df.loc[groups_df['start_time'].isin(pause_split_cluster_start_times)]
                    pause_split_cluster_list_series = []
                    for _, row in pause_split_cluster_rows_df.iterrows():
                        pause_split_cluster_list_series.append(row)
                    split_cluster.append(pause_split_cluster_list_series)
        else:
            split_cluster = [similar_clusters[key]]

        similar_clusters[key] = split_cluster

    return similar_clusters


def get_clusters_statistics(groups_df: pd.DataFrame, clusters: list[list[pd.Series]]) -> list:
    # compute percentage_of_map
    map_length = groups_df.iloc[-1].end_time - groups_df.iloc[0].start_time
    clusters_length = 0
    for cluster in clusters:
        clusters_length += (cluster[-1].end_time - cluster[0].start_time)
    percentage_of_map = round(clusters_length * 100 / map_length, 2)

    # compute avg_group_count_per_cluster
    avg_group_count_per_cluster = 0
    for cluster in clusters:
        avg_group_count_per_cluster += len(cluster)
    avg_group_count_per_cluster /= len(clusters)
    avg_group_count_per_cluster = round(avg_group_count_per_cluster, 2)

    # compute st_dev_group_count_per_cluster
    st_dev_group_count_per_cluster = 0
    for cluster in clusters:
        st_dev_group_count_per_cluster += pow((len(cluster) - avg_group_count_per_cluster), 2)
    st_dev_group_count_per_cluster /= len(clusters)
    st_dev_group_count_per_cluster = math.sqrt(st_dev_group_count_per_cluster)

    # compute avg_obj_count_per_group
    row_count = 0
    avg_obj_count_per_group = 0
    for cluster in clusters:
        if len(cluster) == 1: continue
        for row in cluster:
            avg_obj_count_per_group += row.object_count
            row_count += 1
    avg_obj_count_per_group /= row_count if row_count > 0 else 1
    avg_obj_count_per_group = round(avg_obj_count_per_group, 2)

    # compute st_dev_obj_count_per_group
    row_count = 0
    st_dev_obj_count_per_group = 0
    for cluster in clusters:
        if len(cluster) == 1: continue
        for row in cluster:
            st_dev_obj_count_per_group += pow((row.object_count - avg_obj_count_per_group), 2)
            row_count += 1
    st_dev_obj_count_per_group /= row_count if row_count > 0 else 1
    st_dev_obj_count_per_group = math.sqrt(st_dev_obj_count_per_group)

    # compute n_avg_time_between
    row_count = 0
    n_avg_time_between = 0
    for cluster in clusters:
        if len(cluster) == 1: continue
        prev_end_time = cluster[0].start_time
        for row in cluster:
            n_time_between = (row.start_time - prev_end_time) / row.beat_length
            n_avg_time_between += n_time_between
            prev_end_time = row.end_time
            row_count += 1
    n_avg_time_between /= row_count if row_count > 0 else 1
    n_avg_time_between = round(n_avg_time_between, 2)

    # compute n_st_dev_time_between
    row_count = 0
    n_st_dev_time_between = 0
    for cluster in clusters:
        if len(cluster) == 1: continue
        prev_end_time = cluster[0].start_time
        for row in cluster:
            n_time_between = (row.start_time - prev_end_time) / row.beat_length
            n_st_dev_time_between += pow((n_time_between - n_avg_time_between), 2)
            prev_end_time = row.end_time
            row_count += 1
    n_st_dev_time_between /= row_count if row_count > 0 else 1
    n_st_dev_time_between = math.sqrt(n_st_dev_time_between)

    return [len(clusters), percentage_of_map, avg_group_count_per_cluster, st_dev_group_count_per_cluster, avg_obj_count_per_group, st_dev_obj_count_per_group, n_avg_time_between, n_st_dev_time_between]


def get_split_cluster_context_intervals(groups_df: pd.DataFrame, split_cluster: dict[str: list]):
    context_interval = []
    group_indexes = []
    for group in split_cluster:
        group_indexes.append(group.name)
        
    if group_indexes[0] != 0:
        prev_group = groups_df.iloc[group_indexes[0] - 1]
        if prev_group.next_divisor >= 1:
            context_interval.append(prev_group.name)
        else:
            if len(group_indexes) == 1:
                return [group_indexes[0]]
            else:
                context_interval.append(group_indexes[0]) 
    else:
        if len(group_indexes) == 1:
            return [0]
        else:
            context_interval.append(0)    
        
    if group_indexes[-1] != len(groups_df):
        last_group = groups_df.iloc[group_indexes[-1]]
        if last_group.next_divisor >= 1:
            context_interval.append(last_group.name + 1)
        else:
            if len(group_indexes) == 1:
                return [group_indexes[-1]]
            else:
                context_interval.append(group_indexes[-1]) 
    else:
        if len(group_indexes) == 1:
            return [len(groups_df)]
        else:
            context_interval.append(len(groups_df))
    
    return context_interval


def merge_context_intervals_statistics(context_intervals_statistics: dict) -> dict:
    for cluster in context_intervals_statistics:
        operations = [sum, statistics.mean, statistics.mean, statistics.mean, statistics.mean, statistics.mean, statistics.mean, statistics.mean]
        merged_statistic = [round(func(column), 2) for func, column in zip(operations, zip(*context_intervals_statistics[cluster]))]
        context_intervals_statistics[cluster] = merged_statistic
    return context_intervals_statistics


def get_context_intervals_statistics(groups_df: pd.DataFrame, context_intervals: list) -> dict:
    context_intervals_statistics = {}

    for interval in context_intervals:
        start_index = interval[0]
        end_index = interval[1] if len(interval) != 1 else interval[0]

        context_df = groups_df.iloc[start_index:end_index+1]
        context_similar_clusters = get_similar_clusters(context_df)

        for cluster in context_similar_clusters:
            statistics = get_clusters_statistics(context_df, [context_similar_clusters[cluster]])
            if cluster not in context_intervals_statistics.keys():
                context_intervals_statistics[cluster] = [statistics]
            else:
                context_intervals_statistics[cluster].append(statistics)

    # for type in context_intervals_statistics:
    #     print(type)
    #     for statistic in context_intervals_statistics[type]:
    #         print(statistic)
    #     print()

    return context_intervals_statistics


def parse_clusters(map_id, map_clusters_file):
    groups_df = get_groups_df(map_id, update_entry=True)
    similar_clusters = get_similar_clusters(groups_df)
    split_similar_clusters = get_split_similar_clusters(groups_df, similar_clusters)

    data_matrix = []
    for similar_cluster in split_similar_clusters:
        cluster_details = similar_cluster.split('_')
        cluster_divisor = float(cluster_details[1])
        cluster_count = int(cluster_details[3])

        if cluster_divisor == 4.0 and cluster_count == 8:
            context_intervals = []
            for split_cluster in split_similar_clusters[similar_cluster]:
                context_interval = get_split_cluster_context_intervals(groups_df, split_cluster)
                context_intervals.append(context_interval)
            context_intervals_statistics = get_context_intervals_statistics(groups_df, context_intervals)
            merged_context_intervals_statistics = merge_context_intervals_statistics(context_intervals_statistics)
            clusters_statistics = get_clusters_statistics(groups_df, split_similar_clusters[similar_cluster])
            for key in sorted(list(merged_context_intervals_statistics.keys()), reverse=True):
                print(key, merged_context_intervals_statistics[key])
            print(similar_cluster, clusters_statistics)
            #data_matrix.append(clusters_statistics)
    
    # data_matrix_np = np.array(data_matrix)
    # np.set_printoptions(suppress=True)
    # print(data_matrix_np)

    # map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df['start_time'], groups_df['between_divisor'], groups_df['object_count_n'], c=groups_df['between_divisor'], cmap='Accent')
    # plt.colorbar(map_plot)
    # plt.show()
            
    # sorted_map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df_sorted.index, groups_df_sorted['between_divisor'], groups_df_sorted['object_count_n'], c=groups_df_sorted['between_divisor'], cmap='Accent')
    # plt.colorbar(sorted_map_plot)


def get_clusters_df(map_id, update_entry=False):
    map_clusters_file = os.path.join(get_data_path(), str(map_id) + '_clusters')
    # if not os.path.exists(map_chunks_file):
        # parse_strain(map_id, map_chunks_file)
    return parse_clusters(map_id, map_clusters_file)
    # return pd.read_parquet(map_chunks_file)
