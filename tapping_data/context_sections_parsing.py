import pandas as pd
from tapping_data.sections_parsing import get_sections_dfs_dict
from tapping_data.sections_statistics import get_sections_stats_dict


def get_context_intervals(groups_df: pd.DataFrame, sections_dfs_dict: dict[str: list[pd.DataFrame]], section: str) -> list[list[float, float]]:
    """
    
    """

    context_intervals = []

    for section_df in sections_dfs_dict[section]:
        vertical_section_interval = []
        group_indexes = list(section_df.index.values)
    
        if group_indexes[0] != 0:
            prev_group = groups_df.iloc[group_indexes[0] - 1]
            if prev_group.next_divisor >= 1:
                vertical_section_interval.append(prev_group.name)
            else:
                vertical_section_interval.append(group_indexes[0]) 
        else:
            if len(group_indexes) == 1:
                return [[0]]
            else:
                vertical_section_interval.append(0)    
            
        if group_indexes[-1] != len(groups_df):
            last_group = groups_df.iloc[group_indexes[-1]]
            if last_group.next_divisor >= 1:
                vertical_section_interval.append(last_group.name + 1)
            else:
                if group_indexes[-1] not in vertical_section_interval:
                    vertical_section_interval.append(group_indexes[-1]) 
        else:
            if len(group_indexes) == 1:
                return [[len(groups_df)]]
            else:
                vertical_section_interval.append(len(groups_df))
        
        context_intervals.append(vertical_section_interval)

    return context_intervals


def get_all_context_sections_stats_dict(groups_df: pd.DataFrame) -> dict[str: dict[str: list[float]]]:
    """
        Returns : dict[str: dict[str: list[float]]]
            Dictionary with each section as they key, and as the value another dictionary with every (subsection, [statistics]) pair

        divisor_6.0_count_4
                divisor_6.0_count_4: [0, 327.35, 2, 1, 2]
                divisor_2.0_count_4: [0, 0, 4, 1, 3]
                divisor_1.5_count_4: [0, 325.76, 3.0, 1, 5]
                divisor_1.0_count_4: [0, 0, 3, 1, 6]
        divisor_4.0_count_16
                divisor_4.0_count_16: [0, 176.01, 12.5, 1, 4]
                divisor_2.0_count_16: [0, 0, 24, 1, 5]
                divisor_2.0_count_8: [0, 354.26, 5.5, 1, 7]
                divisor_2.0_count_4: [4.0, 299.76, 2, 1.5, 9]
        divisor_4.0_count_8
                divisor_4.0_count_8: [0, 0, 5, 1, 1]
                divisor_4.0_count_4: [0, 0, 3, 1, 2]
    """
    
    all_context_sections_stats_dict = {}

    sections_dfs_dict = get_sections_dfs_dict(groups_df)
    for section in sections_dfs_dict:
        context_intervals = get_context_intervals(groups_df, sections_dfs_dict, section)
        
        # get all the indices corresponding to the vertical_sections_intervals
        context_indices = []
        for interval in context_intervals:
            start_idx = interval[0]
            end_index = interval[1] if len(interval) != 1 else interval[0]
            context_indices += list(range(start_idx, end_index + 1))

        # get the dataframe associated with the indices
        context_df = groups_df.loc[groups_df.index.isin(context_indices)].copy()

        # compute the sections of that context_df
        context_sections_dfs_dict = get_sections_dfs_dict(context_df, groups_df)

        # compute the statistics for all the sections of that df
        context_sections_stats_dict = get_sections_stats_dict(context_sections_dfs_dict)

        all_context_sections_stats_dict[section] = context_sections_stats_dict
        
    return all_context_sections_stats_dict
        
