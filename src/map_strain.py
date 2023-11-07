import os
import pandas as pd
import matplotlib.pyplot as plt
from map_groups import get_groups_df
from helper import print_t, get_data_path, round_divisor


STRAIN_UPPER_BOUND_MULTIPLIER = 10
STRAIN_THRESHOLD_DIVISOR = 2.0
OBJECT_COUNT_MAX = 1000


def compute_local_strain(strain_df):
    strain_df.loc[strain_df['object_count'] >= OBJECT_COUNT_MAX, 'object_count'] = OBJECT_COUNT_MAX
    strain_df.loc[strain_df['divisor_between_objects'] >= STRAIN_THRESHOLD_DIVISOR, 'local_strain'] = strain_df['object_count'] * strain_df['divisor_between_objects']
    return strain_df


def compute_perceived_strain(strain_df):
    current_strain = 0
    for index, row in strain_df.iterrows():
        if row['divisor_between_objects'] <= 1 or row['divisor_next_group'] < 1:
            current_strain = 0
        elif row['divisor_next_group'] == 1:
            current_strain += row['local_strain']
            strain_df.at[index, 'perceived_strain'] = current_strain
            current_strain /= 2
        else:
            proposed_strain = current_strain + row['local_strain']
            if proposed_strain > row['local_strain'] * STRAIN_UPPER_BOUND_MULTIPLIER:
                proposed_strain = row['local_strain'] * STRAIN_UPPER_BOUND_MULTIPLIER
            current_strain = proposed_strain
            strain_df.at[index, 'perceived_strain'] = current_strain
    return strain_df


def cast_types(strain_df):
    strain_df['divisor_between_objects'] = strain_df['divisor_between_objects'].astype('float32')
    strain_df['divisor_next_group'] = strain_df['divisor_next_group'].astype('float32')
    strain_df['group_count'] = strain_df['group_count'].astype('bool')
    return strain_df


def parse_strain(map_id, map_strain_csv):
    groups_df = get_groups_df(map_id)

    columns = ['bpm', 'object_count', 'divisor_between_objects', 'divisor_next_group', 'local_strain', 'perceived_strain','group_count']
    strain_df = pd.DataFrame(columns=columns)

    strain_df.bpm = 60000 / groups_df.beat_length
    strain_df.object_count = groups_df.object_count
    strain_df.divisor_between_objects = groups_df.beat_length / groups_df.time_between_objects
    strain_df.divisor_between_objects = strain_df['divisor_between_objects'].apply(lambda x: round_divisor(x))
    strain_df.divisor_next_group = groups_df.beat_length / groups_df.time_next_group
    strain_df.divisor_next_group = strain_df['divisor_next_group'].apply(lambda x: round_divisor(x))
    strain_df.local_strain = 0
    strain_df.perceived_strain = 0
    strain_df.group_count = True

    strain_df = compute_local_strain(strain_df)
    strain_df = compute_perceived_strain(strain_df)

    strain_df = cast_types(strain_df)
    strain_df.to_parquet(map_strain_csv, index=False)


def get_strain_df(map_id, update_entry=False):
    map_strain_file = os.path.join(get_data_path(), str(map_id) + '_strain')
    if not os.path.exists(map_strain_file) or update_entry:
        parse_strain(map_id, map_strain_file)
    return pd.read_parquet(map_strain_file)