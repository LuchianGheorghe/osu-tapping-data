import pandas as pd
import numpy as np
from scipy import stats

def compute_statistics(data: list[float]) -> list[float]:
    """
    
    """
    
    if len(set(data)) <= 1:
        value = data[0] if data else 0
        return [value] #,0 , value, value, value, value] 

    summary = stats.describe(data)
    q1 = np.percentile(data, 25)
    q2 = np.percentile(data, 50)
    q3 = np.percentile(data, 75)

    # return [round(summary.mean, 2), round(summary.variance**0.5, 2), summary.minmax[0], q1, q2, q3, summary.minmax[1]]
    # return [round(summary.mean, 2), round(summary.variance**0.5, 2)]
    return [round(summary.mean, 2)]


def get_sections_stats_dict(sections_dfs_dict: dict[str: list[pd.DataFrame]], debug_mode=False) -> dict[str: float]:
    """
    
    """

    total_section_count = 0

    sections_stats_dict = {}
    
    for key in sections_dfs_dict:
        section_group_counts_list = []
        n_time_between_sections_list = []
        group_object_counts_list = []
        n_time_between_groups_list = []

        prev_end_time = 0
        for section_df in sections_dfs_dict[key]:
            first_group = section_df.iloc[0]

            section_group_counts_list.append(section_df.shape[0])
            group_object_counts_list += section_df.object_count.tolist()
            
            if len(sections_dfs_dict[key]) > 1:
                n_time_between_sections_list.append(round((first_group.start_time - prev_end_time) / first_group.beat_length, 2))

            prev_end_time = first_group.start_time
            for _, row in section_df.iterrows():
                n_time_between = round((row.start_time - prev_end_time) / row.beat_length, 2)
                if n_time_between != 0:
                    n_time_between_groups_list.append(n_time_between)
                prev_end_time = row.end_time
            
            total_section_count += 1
        
        n_time_between_groups_stats = compute_statistics(n_time_between_groups_list)
        n_time_between_sections_stats = compute_statistics(n_time_between_sections_list)
        group_object_counts_stats = compute_statistics(group_object_counts_list)   
        section_group_counts_stats = compute_statistics(section_group_counts_list)
        
        if debug_mode:
            print(key)
            print()
            print(f'{n_time_between_groups_list=}')
            print(f'{n_time_between_sections_list=}')
            print(f'{group_object_counts_list=}')
            print(f'{section_group_counts_list=}')
            print()
            print(n_time_between_groups_stats)
            print(n_time_between_sections_stats)
            print(group_object_counts_stats)
            print(section_group_counts_stats)
            print(total_section_count)
            print()

        full_stats = n_time_between_groups_stats + n_time_between_sections_stats + group_object_counts_stats + section_group_counts_stats + [total_section_count]
        sections_stats_dict[key] = full_stats

    return sections_stats_dict
        