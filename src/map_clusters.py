import os, math
import pandas as pd
import matplotlib.pyplot as plt
from map_groups import get_groups_df
from helper import print_t, get_data_path, round_divisor, create_empty_series


def cast_types(clusters_df):
    return clusters_df

def parse_clusters(map_id, map_strain_csv):
    groups_df = get_groups_df(map_id)
    groups_df_sorted = groups_df.sort_values(by=['between_divisor', 'object_count_n'], ascending=False).reset_index(drop=True)

    # map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df['start_time'], groups_df['between_divisor'], groups_df['object_count_n'], c=groups_df['between_divisor'], cmap='Accent')
    # plt.colorbar(map_plot)
    # sorted_map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df_sorted.index, groups_df_sorted['between_divisor'], groups_df_sorted['object_count_n'], c=groups_df_sorted['between_divisor'], cmap='Accent')
    # plt.colorbar(sorted_map_plot)
    # plt.show()

    columns = ['start_time', 'end_time', 'beat_length', 'object_count_n', 'between_divisor', 'group_count', 'time_between_groups']
    clusters_df = pd.DataFrame(columns=columns)
    new_cluster = create_empty_series(columns)

    print(groups_df_sorted.head(25))

    # if it's not the last group of its kind (based on divisor and object_count_n), and it's not the last group in the map
    for idx, cur_row in groups_df_sorted.iterrows():
        if idx == groups_df_sorted.shape[0] - 1:
            break

        next_row = groups_df_sorted.iloc[idx + 1]
    
        if next_row['between_divisor'] == cur_row['between_divisor'] and next_row['object_count_n'] == cur_row['object_count_n']:
            time_next_cluster = next_row['start_time'] - cur_row['start_time']
            if new_cluster.group_count is None:
                new_cluster.time_between_groups = time_next_cluster
                new_cluster.group_count = 1
            else:
                if abs(new_cluster.time_between_groups - time_next_cluster) <= 10000:
                    new_cluster.group_count += 1
                    continue
                if new_cluster.time_between_groups > time_next_cluster:
                    clusters_df = pd.concat([clusters_df, new_cluster.to_frame().T], ignore_index=True)
                    new_cluster = create_empty_series(columns)
                    new_cluster.time_between_groups = time_next_cluster
                    new_cluster.group_count = 1
                else:
                    new_cluster.group_count += 1
                    clusters_df = pd.concat([clusters_df, new_cluster.to_frame().T], ignore_index=True)
                    new_cluster = create_empty_series(columns)
        else:
            if new_cluster.group_count is None:
                new_cluster.group_count = 1
            else:
                new_cluster.group_count += 1
            clusters_df = pd.concat([clusters_df, new_cluster.to_frame().T], ignore_index=True)
            new_cluster = create_empty_series(columns)


    return clusters_df


def get_clusters_df(map_id, update_entry=False):
    map_clusters_file = os.path.join(get_data_path(), str(map_id) + '_clusters')
    # if not os.path.exists(map_chunks_file):
        # parse_strain(map_id, map_chunks_file)
    return parse_clusters(map_id, map_clusters_file)
    #return pd.read_parquet(map_chunks_file)