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
    map_list_sections_stats_df['section_type'] = map_list_sections_stats_df['section_type'].astype('string')
    for count in [4, 8, 16]:
        map_list_sections_stats_df[f'group_object_counts_{count}'] = map_list_sections_stats_df[f'group_object_counts_{count}'].astype('float32')
        map_list_sections_stats_df[f'section_group_counts_{count}'] = map_list_sections_stats_df[f'section_group_counts_{count}'].astype('float32')
        map_list_sections_stats_df[f'n_time_between_groups_{count}'] = map_list_sections_stats_df[f'n_time_between_groups_{count}'].astype('float32')
        map_list_sections_stats_df[f'n_time_between_sections_{count}'] = map_list_sections_stats_df[f'n_time_between_sections_{count}'].astype('float32')
    return map_list_sections_stats_df


def parse_map_list_sections_stats(map_list_file_path: str, target_section_types: list[str], map_list_section_stats_file: str) -> None:
    """

    """

    map_ids = get_map_ids_from_file_path(map_list_file_path)

    columns = ['map_id', 'section_type',
               'n_time_between_groups_16', 'n_time_between_sections_16', 'group_object_counts_16', 'section_group_counts_16', 'total_section_count_16',
               'n_time_between_groups_8', 'n_time_between_sections_8', 'group_object_counts_8', 'section_group_counts_8', 'total_section_count_8',
               'n_time_between_groups_4', 'n_time_between_sections_4', 'group_object_counts_4', 'section_group_counts_4', 'total_section_count_4']
    map_list_section_stats_df = pd.DataFrame(columns=columns)
    
    for map_id in map_ids:
        try:
            sections_stats_dict = get_sections_stats_dict(get_sections_dfs_dict(get_groups_df(map_id)))
        except ValueError as invalid_id:
            print(invalid_id)
        except Exception as e:
            print(map_id, e)       

        for section_type in target_section_types:
            new_row = create_empty_series(columns)
            new_row.map_id = map_id
            new_row.section_type = section_type

            new_row = new_row.fillna(0)

            matching_sections = [actual_section for actual_section in sections_stats_dict if section_type in actual_section]
            if len(matching_sections) == 0: continue
            # print(f'{section_type=}, {map_id=}, {matching_sections=}')

            for matching_section in matching_sections:
                count = matching_section.split('_')[-1]
                new_row[f'group_object_counts_{count}'] = sections_stats_dict[matching_section][0]
                new_row[f'section_group_counts_{count}'] = sections_stats_dict[matching_section][1]
                new_row[f'n_time_between_groups_{count}'] = sections_stats_dict[matching_section][2]
                new_row[f'n_time_between_sections_{count}'] = sections_stats_dict[matching_section][3]
                new_row[f'total_section_count_{count}'] = sections_stats_dict[matching_section][4]
                # print(f'\t{map_id}: {section}: {sections_stats_dict[section]}')

            map_list_section_stats_df = pd.concat([map_list_section_stats_df, new_row.to_frame().T], ignore_index=True)
        # print(new_row)

    map_list_section_stats_df = cast_types(map_list_section_stats_df)
    map_list_section_stats_df.to_parquet(map_list_section_stats_file, index=False)


def get_map_list_sections_stats_df(map_list_file: str, target_section_types: list[str], update_entry: bool = False) -> pd.DataFrame:
    """
    
    """
    
    file_name, _ = os.path.splitext(map_list_file)
    map_list_section_stats_file = os.path.join(get_parsed_lists_path(), str(file_name) + '_parsed.parquet')
    if not os.path.exists(map_list_section_stats_file) or update_entry:
        map_list_file_path = os.path.join(get_lists_path(), map_list_file)
        parse_map_list_sections_stats(map_list_file_path, target_section_types, map_list_section_stats_file)
    return pd.read_parquet(map_list_section_stats_file)