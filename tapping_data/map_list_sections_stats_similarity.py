from tapping_data.context_sections_parsing import get_all_context_sections_stats_dict
from tapping_data.sections_statistics import get_sections_stats_dict
from tapping_data.sections_parsing import get_sections_dfs_dict, visualize_sections
from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df
from tapping_data.helpers import get_map_ids_from_file_path, get_lists_path, create_empty_series
from tapping_data.map_list_sections_stats_parsing import get_map_list_sections_stats_df, parse_map_list_sections_stats

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import time

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

def search_by_cosine_similarity(target_section: str, target_map_id: int, df: pd.DataFrame, top_n: int = 10, target_columns: list[str] = []) -> pd.DataFrame:
	"""
	Returns the most similar maps by cosine similarity to 'target_map_id'.

	Parameters
	----------
	target_map_id : int
		Integer representing the target map id. Will be compared against every other
		map entry in ``df`` when computing cosine similarity by their attributes.

	target_section: str
		String containing which type of sections will be searched. 
		For example, 'divisor_4.0_count_16' will only search maps which 
		have a row with that corresponding type in ``df``.

	df : pd.Dataframe
		Dataframe containing the section statistics of multiple maps, 
		where each row represents a section of map. Structure is:
		map_id, section, 5 x attributes statistically describing the section.

	top_n : int = 10
		Number of similar results to return.

	target_columns : list[str]
		Names of the columns to keep for the cosine similarity comparison.
		Available columns are:
		columns = ['map_id', 'section', 'total_section_count', 'n_time_between_groups', 
		'n_time_between_sections', 'group_object_counts', 'section_group_counts', 'section_all_group_counts']
	"""
	
	df = df[df['section'] == target_section].reset_index()
	target_index = df.index[df['map_id'] == target_map_id].tolist()[0]

	scaler = MinMaxScaler(feature_range=(-1, 1))

	if len(target_columns) == 0:
		n_features_df = df.drop(['map_id', 'section'], axis=1)
	else:
		n_features_df = df.loc[:, target_columns].copy()

	# n_features_df = n_features_df - n_features_df.mean()
	# n_features_df = pd.DataFrame(scaler.fit_transform(n_features_df), columns=n_features_df.columns)

	similarities = cosine_similarity([n_features_df.iloc[target_index]], n_features_df)[0]

	closest_indices = np.argsort(-similarities)[:top_n + 1]
	closest_map_ids = df['map_id'].iloc[closest_indices].values

	return df.iloc[closest_indices]


def get_similar_maps(map_list_file: str = None):
	if map_list_file:
		target_map_id = 345099
		target_section= 'divisor_4.0_count_16'

		columns = ['map_id', 'section', 'total_section_count', 
			'n_time_between_groups', 'n_time_between_sections', 
			'group_object_counts', 'section_group_counts', 'section_all_group_counts']
		target_columns = ['n_time_between_groups', 'section_group_counts', 'section_all_group_counts']

		map_list_df = get_map_list_sections_stats_df(target_section, map_list_file=map_list_file, update_entry=False)

		if target_map_id not in map_list_df.map_id.values:
			new_rows = parse_map_list_sections_stats(target_section, map_ids=[target_map_id])
			map_list_df = pd.concat([map_list_df, new_rows], ignore_index=True)
		

		closest_maps_df = search_by_cosine_similarity(target_section, target_map_id, map_list_df, top_n=50, target_columns=target_columns)
		print(closest_maps_df.sort_values('n_time_between_sections', ascending=False))

		closest_maps_df['diff'] = (closest_maps_df['n_time_between_sections'] - 52.330002).abs()

		
		closest_map_ids = closest_maps_df.sort_values(by='diff').drop('diff', axis=1).index.values

		#closest_map_ids_s = search_by_cosine_similarity(target_map_id, target_section_s, target_subsection_s, map_list_df, closest_map_ids_p, top_n=10)
		#print(closest_map_ids_s)

		#closest_map_ids_intersection = list(set(closest_map_ids_p).intersection(set(closest_map_ids_s)))
		#closest_map_ids_intersection = closest_map_ids_intersection[:11] if len(closest_map_ids_p) > 11 else closest_map_ids_intersection
		#print(closest_map_ids_intersection)

		for map_id in closest_map_ids:
			groups_df = get_groups_df(map_id)
			sections_stats_dict = get_sections_stats_dict(get_sections_dfs_dict(groups_df))
			print(map_id, target_section, sections_stats_dict[target_section])
			# visualize_sections(groups_df)
		
		for map_id in closest_map_ids:
			# webbrowser.open(f'https://osu.ppy.sh/b/{map_id}')
			time.sleep(0.5)

		plt.show()
