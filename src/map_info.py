import pandas as pd
from map_strain import get_strain_df
from map_groups import get_groups_df
from helper import create_empty_series


def cast_types(map_info_df):
    map_info_df['map_id'] = map_info_df['map_id'].astype('int32')
    map_info_df['length'] = map_info_df['length'].astype('float32')
    map_info_df['bpm'] = map_info_df['bpm'].astype('float32')
    map_info_df['aim_rating'] = map_info_df['aim_rating'].astype('float32')
    return map_info_df


def get_map_info_df(map_id):
    columns = ['map_id', 'length', 'bpm', 'aim_rating']
    map_info_df = pd.DataFrame(columns=columns)
    row = create_empty_series(columns)

    strain_df = get_strain_df(map_id)
    bpm_divisor_tuples = strain_df.groupby(['bpm', 'divisor_between_objects']) \
                                    .count()['group_count'] \
                                    .sort_values(ascending=False) \
                                    .index.to_list()

    row['map_id'] = map_id
    row['length'] = get_groups_df(map_id).tail(1)['end_time'].values[0] / 60000
    row['bpm'], _ = bpm_divisor_tuples[0]
    row['aim_rating'] = 0

    map_info_df = pd.concat([map_info_df, row.to_frame().T], ignore_index=True)
    map_info_df = cast_types(map_info_df)

    return map_info_df

