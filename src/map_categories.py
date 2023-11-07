import statistics
import pandas as pd
import matplotlib.pyplot as plt
from helper import print_t, create_empty_series, list_details
from map_strain import get_strain_df
from map_groups import get_groups_df


def cast_types(categories_df):
    for col in ['divisor', 'total_strain', 'finger_control_strain', 'burst_strain', 'stream_strain', 'deathstream_strain']:
        categories_df[col] = categories_df[col].astype('float32')

    for col in ['map_id', 'total_groups', 'finger_control_groups', 'burst_groups', 'stream_groups', 'deathstream_groups']:
        categories_df[col] = categories_df[col].astype('int32')

    return categories_df


def parse_categories(map_id, strain_type='local_strain', strain_df=pd.DataFrame()):
    if strain_type not in ['local_strain', 'perceived_strain']:
        raise ValueError('Invalid value for strain_type ({strain_type}). Should be either "local_strain" or "perceived_strain".')

    strain_df = get_strain_df(map_id)
    
    bpm_divisor_tuples = strain_df.groupby(['bpm', 'divisor_between_objects']) \
                                    .count()['group_count'] \
                                    .sort_values(ascending=False) \
                                    .index.to_list()
    base_bpm, _ = bpm_divisor_tuples[0]


    columns = ['map_id', 'divisor', 
                'total_strain', 
                'finger_control_strain', 'burst_strain', 'stream_strain', 'deathstream_strain',
                'total_groups', 'finger_control_groups', 'burst_groups',  'stream_groups', 'deathstream_groups']
    categories_df = pd.DataFrame(columns=columns)
    
    for bpm_divisor in bpm_divisor_tuples:
        bpm, divisor = bpm_divisor

        if bpm != base_bpm:
            strain_multiplier = min(bpm, base_bpm) / max(bpm, base_bpm)
        else:
            strain_multiplier = 1
        
        if divisor in categories_df['divisor'].values:
            new_row_flag = False
            new_row = categories_df.loc[categories_df['divisor'] == divisor].copy()
        else:
            new_row_flag = True
            new_row = pd.Series(data=[0]*len(columns), index=columns)
            new_row['map_id'] = map_id
            new_row['divisor'] = divisor
            new_row['total_groups'] = strain_df['group_count'].loc[strain_df['divisor_between_objects'] == divisor].count()

        df_by_bpm_divisor = strain_df.loc[(strain_df.bpm == bpm) & (strain_df.divisor_between_objects == divisor)]
        df_by_bpm_divisor = df_by_bpm_divisor[['object_count', strain_type]]

        if divisor in [2, 3, 4, 5, 6, 8]:
            aggs = df_by_bpm_divisor.groupby(['object_count']).agg(['sum', 'count'])
            strain = aggs[strain_type]['sum'].values.sum() * strain_multiplier
            new_row['total_strain'] += strain
            
            types = {}
            types['finger_control'] = (df_by_bpm_divisor.object_count <= 4)
            types['burst'] = (df_by_bpm_divisor.object_count > 4) & (df_by_bpm_divisor.object_count <= 8)
            types['stream'] = (df_by_bpm_divisor.object_count > 8) & (df_by_bpm_divisor.object_count <= 64)
            types['deathstream'] = (df_by_bpm_divisor.object_count > 64)
            for type_name, type_series in types.items():
                aggs = df_by_bpm_divisor.loc[type_series].groupby(['object_count']).agg(['sum', 'count'])
                strain = aggs[strain_type]['sum'].values.sum() * strain_multiplier
                new_row[type_name + '_strain'] += strain                      
                new_row[type_name + '_groups'] += aggs[strain_type]['count'].values.sum()
        else:
            continue
          
        if new_row_flag:
            categories_df = pd.concat([categories_df, new_row.to_frame().T], ignore_index=True)
        else:
            categories_df.loc[categories_df['divisor'] == divisor] = new_row

    categories_df = cast_types(categories_df)
    return categories_df


def get_categories_df(map_id, strain_type):
    '''
    Sums local strain into categories for each relevant divisor (>=2). 
    It's mostly a fancy way to count groups in a BPM-independent way
    and acts as a lower bound to this calculation for perceived strain. 


    df_l = get_categories_df(351752, strain_type='local_strain')
    print(df_l)

    map_id  divisor  total_strain  total_groups  finger_control_strain  burst_strain  stream_strain  deathstream_strain  finger_control_groups  burst_groups  stream_groups  deathstream_groups
0  351752      4.0   5251.653809           354            2663.653809        2356.0          232.0                 0.0                    233           115              6                   0
1  351752      2.0   1514.000000           328            1248.000000         200.0           66.0                 0.0                    308            17              3                   0
    

    df_p = get_categories_df(351752, strain_type='perceived_strain')
    print(df_p)

    map_id  divisor  total_strain  total_groups  finger_control_strain  burst_strain  stream_strain  deathstream_strain  finger_control_groups  burst_groups  stream_groups  deathstream_groups
0  351752      4.0  21594.083984           354           13069.643555   8179.612305     344.828033                 0.0                    233           115              6                   0
1  351752      2.0  12329.895508           328           11561.041016    650.299072     118.555695                 0.0                    308            17              3                   0
    '''

    return parse_categories(map_id, strain_type=strain_type)


def get_categories_df_n(map_id, strain_type):
    df = get_categories_df(map_id, strain_type)

    columns = ['map_id', 'divisor', 
                'total_strain_n', 
                'finger_control_strain_n', 'burst_strain_n', 'stream_strain_n', 'deathstream_strain_n',
                'total_groups_n', 'finger_control_groups_n', 'burst_groups_n',  'stream_groups_n', 'deathstream_groups_n']
    categories_df_n = pd.DataFrame(columns=columns)
    categories_df_n['map_id'] = df['map_id']
    categories_df_n['divisor'] = df['divisor']

    map_length = get_groups_df(map_id).tail(1)['end_time'].values[0] / 60000

    for category in ['total', 'finger_control', 'burst', 'stream', 'deathstream']:
        categories_df_n[f'{category}_strain_n'] = df[f'{category}_strain'].div(df[f'{category}_groups']).round(decimals=2)
        categories_df_n[f'{category}_groups_n'] = df[f'{category}_groups'].div(map_length).round(decimals=2)

    for index, row in categories_df_n.iterrows():
        types_of_strain_count = row[['finger_control_strain_n', 'burst_strain_n', 'stream_strain_n', 'deathstream_strain_n']].count()
        categories_df_n.at[index, 'total_strain_n'] = (row['total_strain_n'] * types_of_strain_count) / 4

    categories_df_n = categories_df_n.fillna(0)
    categories_df_n = categories_df_n.sort_values('divisor', ascending=False)

    return categories_df_n