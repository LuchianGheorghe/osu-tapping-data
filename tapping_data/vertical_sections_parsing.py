import pandas as pd
from tapping_data.sections_parsing import get_sections_dfs_dict


def get_vertical_sections_intervals(groups_df: pd.DataFrame, sections_dfs_dict: dict[str: list[pd.DataFrame]], section: str) -> list[list[float, float]]:
    """
    
    """

    intervals = []

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
                return [0]
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
                return [len(groups_df)]
            else:
                vertical_section_interval.append(len(groups_df))
        
        intervals.append(vertical_section_interval)

    return intervals


def get_vertical_sections(groups_df: pd.DataFrame) -> dict:
    sections_dfs_dict = get_sections_dfs_dict(groups_df)
    for section in sections_dfs_dict:
        vertical_sections_intervals = get_vertical_sections_intervals(groups_df, sections_dfs_dict, section)
        print(section, vertical_sections_intervals)
        # get all the indices for the section_context_interval
        # put all groups of the corresponding indices in a df
        # compute the sections of that df
        # compute the statistics for all the sections of that df

    # for interval in context_intervals:
    #     start_index = interval[0]
    #     end_index = interval[1] if len(interval) != 1 else interval[0]

    #     context_df = groups_df.iloc[start_index:end_index+1]
    #     context_similar_clusters = get_similar_clusters(context_df)

    #     for cluster in context_similar_clusters:
    #         statistics = get_clusters_statistics(context_df, [context_similar_clusters[cluster]])
    #         if cluster not in context_intervals_statistics.keys():
    #             context_intervals_statistics[cluster] = [statistics]
    #         else:
    #             context_intervals_statistics[cluster].append(statistics)

    # for type in context_intervals_statistics:
    #     print(type)
    #     for statistic in context_intervals_statistics[type]:
    #         print(statistic)
    #     print()

    # return context_intervals_statistics