import os
import pandas as pd
import requests
from helper import get_data_path, round_divisor, create_empty_series, get_maps_path

from beatmap_reader import BeatmapIO

def cast_types(objects_df):
	objects_df['start_time'] = objects_df['start_time'].astype('int32')
	objects_df['end_time'] = objects_df['end_time'].astype('int32')
	objects_df['beat_length'] = objects_df['beat_length'].astype('float32')
	objects_df['time_next_object'] = objects_df['time_next_object'].astype('float32')

	return objects_df


def get_beatmap_data(map_id):
	map_path = os.path.join(get_maps_path(), str(map_id) + '.osu')
	if not os.path.exists(map_path):
		url = f'https://osu.ppy.sh/osu/{map_id}'
		response = requests.get(url)
		if response.text != '':
			with open(map_path, 'wb') as map:
				map.write(response.content)
		else:
			raise ValueError(f'Invalid beatmap ID: {map_id}')
	return BeatmapIO.open_beatmap(map_path)


def parse_objects(map_id, map_objects_file):
	try:
		beatmap = get_beatmap_data(map_id)
	except BeatmapIO.BeatmapIOException as e:
		raise e

	columns = ['start_time', 'end_time', 'beat_length', 'time_next_object']
	objects_df = pd.DataFrame(columns=columns)
	new_object = create_empty_series(columns)
	
	t_idx = 0
	for idx, hitobject in enumerate(beatmap.hitobjects):
		for i in range(t_idx + 1, len(beatmap.timing_points)):
			if beatmap.timing_points[i].offset <= hitobject.start_time():
				t_idx = i
			else:
				break
		timing_point = beatmap.timing_points[t_idx]
		beat_length = timing_point.beat_length
		
		if idx != len(beatmap.hitobjects) - 1:
			time_next_object = beatmap.hitobjects[idx + 1].start_time() - hitobject.start_time()
			time_next_object = (beat_length / round_divisor(beat_length / time_next_object)) if (beat_length > time_next_object) else (beat_length * round_divisor(time_next_object / beat_length))
		else:
			time_next_object = 0
		
		new_object['start_time'] = hitobject.start_time()
		new_object['end_time'] = hitobject.end_time()
		new_object['beat_length'] = beat_length
		new_object['time_next_object'] = time_next_object

		objects_df = pd.concat([objects_df, new_object.to_frame().T], ignore_index=True)
		new_object = create_empty_series(columns)

	objects_df = cast_types(objects_df)
	objects_df.to_parquet(map_objects_file, index=False)


def get_objects_df(map_id, update_entry=False):
	map_objects_file = os.path.join(get_data_path(), str(map_id) + '_objects')
	if not os.path.exists(map_objects_file) or update_entry:
		parse_objects(map_id, map_objects_file)
	return pd.read_parquet(map_objects_file)