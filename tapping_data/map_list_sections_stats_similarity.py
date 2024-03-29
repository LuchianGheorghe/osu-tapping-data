from tapping_data.context_sections_parsing import get_all_context_sections_stats_dict
from tapping_data.sections_statistics import get_sections_stats_dict
from tapping_data.sections_parsing import get_sections_dfs_dict, visualize_sections
from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df
from tapping_data.helpers import get_map_ids_from_file_path, get_lists_path, create_empty_series
from tapping_data.map_list_sections_stats_parsing import get_map_list_sections_stats_df

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import time


def search_by_cosine_similarity(target_map_id: int, section_type: str, section_subtype: list[int], df: pd.DataFrame, subset_map_ids: list[int] = None, top_n: int = 25) -> list[int]:
	"""
	Returns the most similar maps by cosine similarity to 'target_map_id'.

	Parameters
	----------
	target_map_id : int
		Integer representing the target map id. Will be compared against every other
		map entry in ``df`` when computing cosine similarity by their attributes.

	section_type: str
		String containing which type of sections will be searched. 
		For example, 'divisor_4.0' will only search maps which 
		have a row with that corresponding type in ``df``.

	section_subtype : list[int]
		A list which can contain any of [4, 8, 16] in a given order. This can be used
		to specify the priority for which subsections to perform cosine similarity.

	df : pd.Dataframe
		Dataframe containing the section statistics of multiple maps, 
		where each row represents a section of map. Structure is:
		map_id, section_type, 5 x attributes statistically describing the section.

	subset_map_ids : list[int] = None
		List of map ids to optionally filter ``df`` by. 

	top_n : int = 25
		Number of similar results to return.
	"""
	
	if target_map_id not in df['map_id'].values:
		print("Target map id not found in the dataframe")
		return
	
	df = df[df['section_type'] == section_type].reset_index()

	if subset_map_ids is not None:
		df = df[df['map_id'].isin(subset_map_ids)].reset_index()
	
	target_index = df.index[df['map_id'] == target_map_id].tolist()[0]

	subtypes_to_ignore = [subtype for subtype in [4, 8, 16] if subtype not in section_subtype]
	cols_to_drop = []
	for col in df.columns:
		if col in ['map_id', 'section_type', 'index']: continue
		col_subtype = int(col.split('_')[-1])
		if col_subtype in subtypes_to_ignore: 
			cols_to_drop.append(col)

	n_features_df = df.drop(['map_id', 'section_type'] + cols_to_drop, axis=1)
	n_features_df = n_features_df - n_features_df.mean()

	similarities = cosine_similarity([n_features_df.iloc[target_index]], n_features_df)[0]

	closest_indices = np.argsort(-similarities)[:top_n + 1]
	closest_map_ids = df['map_id'].iloc[closest_indices].values

	return closest_map_ids


def get_similar_maps(map_list_file: str = None):
	
	if map_list_file:
		target_map_id = 345099

		target_section_p = 'divisor_4.0'
		target_subsection_p = [4, 8, 16]

		target_section_s = 'divisor_2.0'
		target_subsection_s = [4, 8, 16]

		target_section_types = ['divisor_4.0', 'divisor_2.0']
		map_list_df = get_map_list_sections_stats_df(map_list_file, target_section_types, update_entry=False)
		# map_list_section_stats_df_secondary = get_map_list_sections_stats_df(map_list_file, target_section_secondary, update_entry=False)
		# print(map_list_section_stats_df)
		print(map_list_df)

		closest_map_ids_p = search_by_cosine_similarity(target_map_id, target_section_p, target_subsection_p, map_list_df, top_n=10)
		print(closest_map_ids_p)
		
		#closest_map_ids_s = search_by_cosine_similarity(target_map_id, target_section_s, target_subsection_s, map_list_df, closest_map_ids_p, top_n=10)
		#print(closest_map_ids_s)

		#closest_map_ids_intersection = list(set(closest_map_ids_p).intersection(set(closest_map_ids_s)))
		#closest_map_ids_intersection = closest_map_ids_intersection[:11] if len(closest_map_ids_p) > 11 else closest_map_ids_intersection
		#print(closest_map_ids_intersection)

		for map_id in closest_map_ids_p:
			groups_df = get_groups_df(map_id)
			sections_stats_dict = get_sections_stats_dict(get_sections_dfs_dict(groups_df))
			
			matching_sections = [existing_section for existing_section in sections_stats_dict if target_section_p in existing_section or target_section_s in existing_section]
			for section in matching_sections:
				print(map_id, section, sections_stats_dict[section])
			print()
			
			visualize_sections(groups_df)
		
		for map_id in closest_map_ids_p:
			# webbrowser.open(f'https://osu.ppy.sh/b/{map_id}')
			time.sleep(0.5)

		plt.show()
