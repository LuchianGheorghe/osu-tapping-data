import pandas as pd
import numpy as np
from scipy import stats

def compute_statistics(data: list[float]) -> list[float]:
    """
    
    """

    if len(data) == 1 or len(set(data)) == 1:
        value = data[0]
        return [value, 0, value, value, value, value] 

    summary = stats.describe(data)
    q1 = np.percentile(data, 25)
    q2 = np.percentile(data, 50)
    q3 = np.percentile(data, 75)

    return [round(summary.mean, 2), round(summary.variance**0.5, 2), summary.minmax[0], q1, q2, q3, summary.minmax[1]]


def describe_similar_groups(similar_groups_dfs_dict: dict[str: list[pd.DataFrame]]) -> list[float]:
    """
    
    """
    
    for key in similar_groups_dfs_dict:
        if not ('4.0' in key):
            continue
        print(key)
        # print(similar_groups_dfs_dict[key])

        n_time_between_values = []
        object_count_values = []
        section_length_values = []

        for similar_group_df in similar_groups_dfs_dict[key]:

            section_length_values.append(similar_group_df.shape[0])
            object_count_values += similar_group_df.object_count.tolist()

            prev_end_time = similar_group_df.iloc[0].start_time
            for _, row in similar_group_df.iterrows():
                n_time_between = round((row.start_time - prev_end_time) / row.beat_length, 2)
                if n_time_between != 0: n_time_between_values.append(n_time_between)
                prev_end_time = row.end_time
            if len(n_time_between_values) == 0:
                n_time_between_values.append(0)
        
        print()
        print(f'{n_time_between_values=}')
        print(f'{object_count_values=}')
        print(f'{section_length_values=}')
        print()
        print(compute_statistics(n_time_between_values))
        print(compute_statistics(object_count_values))
        print(compute_statistics(section_length_values))
        print()