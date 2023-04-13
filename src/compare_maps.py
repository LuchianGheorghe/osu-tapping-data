import os
import pandas as pd
import matplotlib.pyplot as plt

from map_objects import get_objects_df
from map_groups import get_groups_df
from map_strain import get_strain_df
from map_chunks import get_chunks_df
from map_categories import get_categories
from helper import parse_list, list_details


def compare_maps(map_ids):
    for map_id in map_ids:
        # categories_df = get_categories(map_id).sort_values('divisor')
        # categories_df = categories_df.loc[(categories_df['divisor'] == 2) | (categories_df['divisor'] == 4)]
        # print(categories_df[['map_id', 'divisor', 'total_strain', 'finger_control_strain', 'burst_strain', 'stream_strain', 'deathstream_strain']])

        chunks_df = get_chunks_df(map_id).sort_values('divisor')
        # chunks_df = chunks_df.loc[(chunks_df['divisor'] == 2) | (chunks_df['divisor'] == 4)]
        print(chunks_df[['map_id', 'divisor', 'total_strain', 'finger_control_strain', 'burst_strain', 'stream_strain', 'deathstream_strain']])

