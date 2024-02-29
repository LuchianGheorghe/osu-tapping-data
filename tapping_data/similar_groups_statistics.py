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


def get_sections_statistics(similar_groups_dfs_dict: dict[str: list[pd.DataFrame]]) -> list[float]:
    """
    
    """
    
    for key in similar_groups_dfs_dict:
        if not (('16' in key or '8' in key) and '4.0' in key):
            continue
        print(key)
        # print(similar_groups_dfs_dict[key])

        section_group_counts_list = []
        n_time_between_sections_list = []
        group_object_counts_list = []
        n_time_between_groups_list = []

        prev_end_time = 0
        for section_df in similar_groups_dfs_dict[key]:

            # print(section_df)

            first_group = section_df.iloc[0]

            section_group_counts_list.append(section_df.shape[0])
            n_time_between_sections_list.append(round((first_group.start_time - prev_end_time) / first_group.beat_length, 2))
            group_object_counts_list += section_df.object_count.tolist()

            prev_end_time = first_group.start_time
            for _, row in section_df.iterrows():
                n_time_between = round((row.start_time - prev_end_time) / row.beat_length, 2)
                if n_time_between != 0: 
                    n_time_between_groups_list.append(n_time_between)
                prev_end_time = row.end_time
        
        print()
        print(f'{section_group_counts_list=}')
        print(f'{n_time_between_sections_list=}')
        print(f'{group_object_counts_list=}')
        print(f'{n_time_between_groups_list=}')
        print()
        print(compute_statistics(section_group_counts_list))
        print(compute_statistics(n_time_between_sections_list))
        print(compute_statistics(group_object_counts_list))
        print(compute_statistics(n_time_between_groups_list))
        print()