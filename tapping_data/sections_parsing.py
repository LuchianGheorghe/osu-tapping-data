from tapping_data.helpers import round_divisor
import pandas as pd
import numpy as np
import jenkspy
import bisect
import math
import matplotlib.pyplot as plt


def visualize_sections_old(groups_df: pd.DataFrame) -> None:
    """
    
    """
    
    map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df['start_time'], groups_df['between_divisor'], groups_df['object_count_n'], c=groups_df['between_divisor'], cmap='Accent')
    plt.colorbar(map_plot)
    plt.show(block=False)


def visualize_sections(groups_df: pd.DataFrame) -> None:
    """
    Visualize sections with a 3D scatter plot.
    
    Args:
    - groups_df (pd.DataFrame): A DataFrame containing the columns 'start_time', 
                                'between_divisor', 'object_count_n', and 'between_divisor' used for coloring.
    """
    
    # Create a new figure for each plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Generate the scatter plot
    map_plot = ax.scatter(groups_df['start_time'], groups_df['between_divisor'], groups_df['object_count_n'], c=groups_df['between_divisor'], cmap='Accent')
    
    # Add a color bar for reference
    plt.colorbar(map_plot)
    
    # Display the plot
    plt.show(block=False)


def visualize_sections_sorted(groups_df: pd.DataFrame) -> None:
    """
    
    """
    
    groups_df_sorted = groups_df.sort_values(by=['between_divisor', 'object_count_n'], ascending=False).reset_index(drop=True)
            
    sorted_map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df_sorted.index, groups_df_sorted['between_divisor'], groups_df_sorted['object_count_n'], c=groups_df_sorted['between_divisor'], cmap='Accent')
    plt.colorbar(sorted_map_plot)
    plt.show()


def get_sections_by_divisor_and_count_n(groups_df: pd.DataFrame) -> dict[str: list[pd.DataFrame]]:
    """
    
    """
    
    groups_df_sorted = groups_df.sort_values(by=['between_divisor', 'object_count_n'], ascending=False).reset_index(drop=True)
    
    sections = {}
    columns = groups_df.columns
    new_similar = pd.DataFrame(columns=columns)

    for i, curr_row in groups_df_sorted.iterrows():
        key = f'divisor_{round_divisor(curr_row.between_divisor)}_count_{int(curr_row.object_count_n)}'
        
        if new_similar.empty:
            new_similar = curr_row.to_frame().T.reset_index(drop=True)

        if i == groups_df_sorted.shape[0] - 1:
            sections[key] = [new_similar]
            break

        next_row = groups_df_sorted.iloc[i+1]
        if next_row['between_divisor'] == curr_row['between_divisor'] and next_row['object_count_n'] == curr_row['object_count_n']:
            new_similar = pd.concat([new_similar, next_row.to_frame().T], ignore_index=True)
        else:
            sections[key] = [new_similar]
            new_similar = pd.DataFrame(columns=columns)

    return sections


def split_list_at_values(sorted_list, split_values):
    """
    
    """
    
    split_indices = [bisect.bisect_right(sorted_list, val) for val in split_values]
    split_indices = [0] + split_indices + [len(sorted_list)]

    return [sorted_list[split_indices[i]:split_indices[i + 1]] for i in range(len(split_indices) - 1) if split_indices[i] != split_indices[i + 1]]


def split_sections_by_variance(start_times: list[float]) -> list[list[float]]:
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


def split_sections_by_pauses(groups_df: pd.DataFrame, start_times: list[list[float]], all_groups_df: pd.DataFrame = None) -> list[list[float]]:
    """
        all_groups_df: used for the case of context_sections, which reconstruct groups_df to only contain the relevant groups. Otherwise this would split differently and give different values
    """
    
    if all_groups_df is not None:
        groups_df = all_groups_df

    pause_points = groups_df[groups_df.next_divisor < 1]['start_time'].to_list()

    pause_split_groups_start_times = []
    for split_group in start_times:
        pause_split_group = split_list_at_values(split_group, pause_points)
        pause_split_groups_start_times += pause_split_group

    return pause_split_groups_start_times

    
def get_sections_split_dfs(groups_df: pd.DataFrame, start_times: list[list[float]]):
    """
    
    """
    
    similar_split_group_dfs = []

    for split_group_start_times in start_times:
        split_group_df = groups_df.loc[groups_df['start_time'].isin(split_group_start_times)]
        similar_split_group_dfs.append(split_group_df)

    return similar_split_group_dfs


def split_sections(groups_df: pd.DataFrame, sections: dict[str: list[pd.DataFrame]], all_groups_df: pd.DataFrame = None) -> dict[str: list[pd.DataFrame]]:
    """
        Todo: instead of using start_times, create a list of the times between the groups and check the variance based on that.
    """

    for key in sections:
        start_times = sections[key][0]['start_time'].to_list()

        if len(start_times) == 1:
            sections[key] = [groups_df.loc[groups_df['start_time'].isin(start_times)]]
        else:
            split_groups_start_times = split_sections_by_variance(start_times)
            split_groups_start_times = split_sections_by_pauses(groups_df, split_groups_start_times, all_groups_df)
            sections[key] = get_sections_split_dfs(groups_df, split_groups_start_times)

    return sections


def get_sections_dfs_dict(groups_df: pd.DataFrame, all_groups_df: pd.DataFrame = None) -> dict[str: list[pd.DataFrame]]:
    """
        Divides a groups_df into
    """

    sections = get_sections_by_divisor_and_count_n(groups_df)
    sections = split_sections(groups_df, sections, all_groups_df)

    return sections
