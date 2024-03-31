from tapping_data.helpers import get_downloaded_maps_path, create_empty_series, get_lists_path, get_parsed_lists_path, get_map_ids_from_file_path
from tapping_data.sections_statistics import get_sections_stats_dict
from tapping_data.sections_parsing import get_sections_dfs_dict
from tapping_data.groups_parsing import get_groups_df

import os
import pandas as pd


def cast_types(map_list_sections_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
        
    """

    map_list_sections_stats_df['map_id'] = map_list_sections_stats_df['map_id'].astype('int32')
    map_list_sections_stats_df['section'] = map_list_sections_stats_df['section'].astype('string')
    map_list_sections_stats_df[f'group_object_counts'] = map_list_sections_stats_df[f'group_object_counts'].astype('float32')
    map_list_sections_stats_df[f'section_group_counts'] = map_list_sections_stats_df[f'section_group_counts'].astype('float32')
    map_list_sections_stats_df[f'n_time_between_groups'] = map_list_sections_stats_df[f'n_time_between_groups'].astype('float32')
    map_list_sections_stats_df[f'n_time_between_sections'] = map_list_sections_stats_df[f'n_time_between_sections'].astype('float32')
    return map_list_sections_stats_df


def parse_map_list_sections_stats(target_section: str, map_ids: list[str] = [], map_list_file_path: str = None, map_list_section_stats_file: str = None) -> pd.DataFrame:
    """

    """
    if map_list_file_path is not None:
        map_ids += get_map_ids_from_file_path(map_list_file_path)

    columns = ['map_id', 'section', 'n_time_between_groups', 'n_time_between_sections', 'group_object_counts', 'section_group_counts', 'total_section_count']
    map_list_section_stats_df = pd.DataFrame(columns=columns)
    
    for map_id in map_ids:
        try:
            sections_stats_dict = get_sections_stats_dict(get_sections_dfs_dict(get_groups_df(map_id)))
        except ValueError as invalid_id:
            print(invalid_id)
        except Exception as e:
            print(map_id, e)

        if target_section not in sections_stats_dict:
            continue

        new_row = create_empty_series(columns)
        new_row.map_id = map_id
        new_row.section = target_section

        new_row[f'group_object_counts'] = sections_stats_dict[target_section][0]
        new_row[f'section_group_counts'] = sections_stats_dict[target_section][1]
        new_row[f'n_time_between_groups'] = sections_stats_dict[target_section][2]
        new_row[f'n_time_between_sections'] = sections_stats_dict[target_section][3]
        new_row[f'total_section_count'] = sections_stats_dict[target_section][4]
        # print(f'\t{map_id}: {section}: {sections_stats_dict[section]}')

        new_row = new_row.fillna(0)

        map_list_section_stats_df = pd.concat([map_list_section_stats_df, new_row.to_frame().T], ignore_index=True)
        # print(new_row)

    map_list_section_stats_df = cast_types(map_list_section_stats_df)
    
    if map_list_section_stats_file is not None:
        map_list_section_stats_df.to_parquet(map_list_section_stats_file, index=False)

    return map_list_section_stats_df


def get_map_list_sections_stats_df(target_section: str, map_ids: list[str] = [], map_list_file: str = None, update_entry: bool = False) -> pd.DataFrame:
    """

    """
    
    file_name, _ = os.path.splitext(map_list_file)
    map_list_section_stats_file = os.path.join(get_parsed_lists_path(), f'{str(file_name)}_{target_section}_parsed.parquet')
    if not os.path.exists(map_list_section_stats_file) or update_entry:
        map_list_file_path = os.path.join(get_lists_path(), map_list_file)
        return parse_map_list_sections_stats(target_section, map_ids, map_list_file_path, map_list_section_stats_file)
    return pd.read_parquet(map_list_section_stats_file)