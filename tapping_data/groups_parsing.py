from tapping_data.objects_parsing import get_objects_df
from tapping_data.helpers import create_empty_series, get_parsed_maps_path, round_divisor

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def visualize_all_groups(map_id: int) -> None:
	groups_df = get_groups_df(map_id)

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	map_plot = ax.scatter(groups_df['start_time'], groups_df['between_divisor'], groups_df['object_count_n'], c=groups_df['between_divisor'], cmap='Accent')

	plt.title(f'{map_id=}')
	plt.colorbar(map_plot)
	plt.show(block=False)


def visualize_select_group(map_id: int, between_divisor: float, object_count_n: int) -> None:
	groups_df = get_groups_df(map_id)
	
	select_groups_filter = (groups_df['between_divisor'] == between_divisor) & (groups_df['object_count_n'] == object_count_n)
	select_groups_df = groups_df.loc[select_groups_filter]

	plt.figure()
	plt.title(f'{map_id=}, group_type=divisor_{between_divisor}_count_{object_count_n}')
	plt.scatter(select_groups_df['start_time'], [1] * len(select_groups_df), c='black')
	
	plt.show(block=False)


def visualize_select_group_n_samples(map_ids: list, n_samples: int = 10, open_links: bool = False):
	pass


def cast_types(df_groups):
	df_groups['start_time'] = df_groups['start_time'].astype('int32')
	df_groups['end_time'] = df_groups['end_time'].astype('int32')
	df_groups['beat_length'] = df_groups['beat_length'].astype('float32')
	df_groups['time_between_objects'] = df_groups['time_between_objects'].astype('float32')
	df_groups['time_next_group'] = df_groups['time_next_group'].astype('float32')
	df_groups['object_count'] = df_groups['object_count'].astype('int16')
	df_groups['object_count_n'] = df_groups['object_count_n'].astype('int16')
	df_groups['between_divisor'] = df_groups['between_divisor'].astype('float32')
	df_groups['next_divisor'] = df_groups['next_divisor'].astype('float32')
	return df_groups


def normalize_beat_length(beat_length):
    while beat_length < 185:
        beat_length *= 2
    while beat_length > 500:
        beat_length /= 2
    return beat_length


def normalize_count(object_count_row):
	if object_count_row <= 4:
		return 4  # 1-4
	elif object_count_row > 4 and object_count_row <= 8:
		return 8  # 5-8
	else:
		return 16  # 16+


def parse_groups(map_id, map_groups_file):
	objects_df = get_objects_df(map_id)

	columns = ['start_time', 'end_time', 'beat_length', 'time_between_objects', 'time_next_group', 'object_count', 'object_count_n', 'between_divisor', 'next_divisor']
	groups_df = pd.DataFrame(columns=columns)
	new_group = create_empty_series(columns)

	for time_next_object in objects_df['time_next_object']:
		if new_group.object_count is None:
			new_group.time_between_objects = time_next_object
			new_group.object_count = 1
		else:
			if abs(new_group.time_between_objects - time_next_object) <= 1:
				new_group.object_count += 1
				continue
			if new_group.time_between_objects <= time_next_object or time_next_object == 0:
				new_group.object_count += 1
				groups_df = pd.concat([groups_df, new_group.to_frame().T], ignore_index=True)
				new_group = create_empty_series(columns)
			else:
				groups_df = pd.concat([groups_df, new_group.to_frame().T], ignore_index=True)
				new_group = create_empty_series(columns)
				new_group.time_between_objects = time_next_object
				new_group.object_count = 1

	first_obj_index = -1
	last_obj_index = -1
	for _, group_row in groups_df.iterrows():
		first_obj_index = last_obj_index + 1
		last_obj_index = first_obj_index + group_row.object_count - 1
		group_row.start_time = objects_df.iloc[first_obj_index].start_time
		group_row.beat_length = normalize_beat_length(objects_df.iloc[first_obj_index].beat_length)
		group_row.end_time = objects_df.iloc[last_obj_index].start_time
		group_row.time_next_group = objects_df.iloc[last_obj_index].time_next_object

	groups_df.object_count_n = groups_df['object_count'].apply(normalize_count)

	groups_df.between_divisor = (groups_df.beat_length / groups_df.time_between_objects).apply(lambda x: round_divisor(x))
	groups_df.next_divisor = (groups_df.beat_length / groups_df.time_next_group).apply(lambda x: round_divisor(x))
	groups_df.iloc[-1, groups_df.columns.get_loc('next_divisor')] = 0

	groups_df = cast_types(groups_df)
	groups_df.to_parquet(map_groups_file, index=False)


def get_groups_df(map_id, update_entry=False):
	map_groups_file = os.path.join(get_parsed_maps_path(), str(map_id) + '_groups')
	if not os.path.exists(map_groups_file) or update_entry:
		parse_groups(map_id, map_groups_file)
	return pd.read_parquet(map_groups_file)