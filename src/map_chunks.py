import os, math
import pandas as pd
import matplotlib.pyplot as plt
from map_groups import get_groups_df
from map_strain import get_strain_df
from map_categories import get_categories_df
from helper import print_t, get_data_path, round_divisor


def cast_types(chunks_df):
    chunks_df['map_id'] = chunks_df['map_id'].astype('int32')
    return chunks_df


def cv_multiplier(cv):
    # write a comment about this random looking value
    if cv == 0 or cv >= 1:
        return 1
    elif cv < 0.577:
        return 2 * 0.577 - cv
    return cv


def parse_chunks(map_id, map_strain_csv):
    strain_df = get_strain_df(map_id)

    chunks_df = pd.DataFrame()

    # think of a way to redo this using indexes only instead of copying rows as dicsts into lists and recreating strain_df from those dicts, etc
    chunks = []
    current_chunk = []
    for _, strain in strain_df.iterrows():
        current_chunk.append(strain.to_dict())
        if strain['divisor_between_objects'] <= 1 or strain['divisor_next_group'] < 1:
            chunks.append(current_chunk)
            current_chunk = []
    if chunks == [] or current_chunk != []:
        chunks.append(current_chunk)

    for chunk in chunks:
        chunk_strain_df = pd.DataFrame(chunk)
        if chunk_strain_df['local_strain'].sum() == 0:
            continue

        chunk_categories_df = get_categories_df(map_id, chunk_strain_df)
        #if chunk_categories_df['total_groups'].sum() > 1:
            #print(chunk_categories_df[['total_strain', 'total_groups', 'finger_control_strain', 'burst_strain', 'stream_strain', 'deathstream_strain','finger_control_cv', 'burst_cv', 'stream_cv', 'deathstream_cv']])

        if chunks_df.empty:
            chunks_df = chunk_categories_df
        else:
            chunks_df = pd.concat([chunks_df, chunk_categories_df], ignore_index=True)
    
    for category in ['finger_control', 'burst', 'stream', 'deathstream']:
            condition = chunks_df[category + '_groups'] > 0
            chunks_df.loc[condition, category + '_cv'] = chunks_df.loc[condition, category + '_cv'].apply(lambda x: cv_multiplier(x))
            chunks_df.loc[condition, category + '_strain'] = (chunks_df.loc[condition, category + '_strain'] / chunks_df.loc[condition, category + '_cv']).round()

    chunks_df = chunks_df.groupby('divisor').agg(sum).reset_index()

    chunks_df['map_id'] = map_id
    chunks_df['total_strain'] = 0
    for category in ['finger_control', 'burst', 'stream', 'deathstream']:
            condition = chunks_df[category + '_groups'] > 0
            chunks_df.loc[condition, 'total_strain'] += chunks_df.loc[condition, category + '_strain']
    
    return chunks_df


def get_chunks_df(map_id):
    map_chunks_file = os.path.join(get_data_path(), str(map_id) + '_chunks')
    # if not os.path.exists(map_chunks_file):
        # parse_strain(map_id, map_chunks_file)
    return parse_chunks(map_id, map_chunks_file)
    #return pd.read_parquet(map_chunks_file)