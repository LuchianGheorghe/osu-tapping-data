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