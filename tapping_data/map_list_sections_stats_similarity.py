from tapping_data.groups_parsing import get_groups_df, visualize_all_groups
from tapping_data.helpers import get_map_ids_from_file_path, get_lists_path, create_empty_series
from tapping_data.map_list_sections_stats_parsing import get_map_list_sections_stats_df, parse_map_list_sections_stats

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import time

from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import MinMaxScaler

from sklearn.cluster import KMeans


def search_by_cosine_similarity(target_section: str, target_map_id: int, df: pd.DataFrame, top_n: int = 10, target_columns: list[str] = []) -> tuple[pd.DataFrame, list[int]]:
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

	return df.iloc[closest_indices], closest_map_ids


def get_similar_maps(target_map_id: int, target_section: str, map_list_file: str, visualize: bool = False, open_links: bool = False) -> None:
	"""
	
	"""

	visualize = True
	open_links = False

	original_columns = ['map_id', 'section', 'total_section_count', 'n_time_between_groups', 'n_time_between_sections', 'group_object_counts', 'section_group_counts', 'section_all_group_counts']
	target_columns = ['total_section_count', 'n_time_between_groups', 'n_time_between_sections', 'group_object_counts', 'section_group_counts', 'section_all_group_counts']

	map_list_df = get_map_list_sections_stats_df(target_section, map_list_file=map_list_file, update_entry=False)

	if target_map_id not in map_list_df.map_id.values:
		new_rows = parse_map_list_sections_stats(target_section, map_ids=[target_map_id])
		map_list_df = pd.concat([map_list_df, new_rows], ignore_index=True)

	closest_maps_df, closest_map_ids = search_by_cosine_similarity(target_section, target_map_id, map_list_df, top_n=5, target_columns=target_columns)

	for col in ['map_id', 'section'] + target_columns:
		original_columns.remove(col)
	columns_reordered = ['map_id', 'section'] + target_columns + original_columns

	#closest_maps_df['diff'] = (closest_maps_df['group_object_counts'] - closest_maps_df.iloc[0]['group_object_counts']).abs()
	#closest_maps_df.sort_values(by='diff').drop('diff', axis=1)

	print(closest_maps_df[columns_reordered].to_string(index=False))

	if visualize:
		for map_id in closest_map_ids:
			groups_df = get_groups_df(map_id)
			visualize_all_groups(groups_df)
	
	if open_links:
		for map_id in closest_map_ids:
			webbrowser.open(f'https://osu.ppy.sh/b/{map_id}')
			time.sleep(0.5)

	plt.show()


def target_section_clustering(target_section: str, map_list_file: str) -> None:
	"""
	
	"""

	map_list_df = get_map_list_sections_stats_df(target_section, map_list_file=map_list_file, update_entry=False)
	n_features_df = map_list_df.drop(['map_id', 'section'], axis=1)

	# inertias = []
	# for i in range(1,11):
	# 	kmeans = KMeans(n_clusters=i)
	# 	kmeans.fit(n_features_df[['total_section_count', 'n_time_between_groups', 'section_group_counts', 'section_all_group_counts']])
	# 	inertias.append(kmeans.inertia_)

	# plt.plot(range(1,11), inertias, marker='o')
	# plt.title('Elbow method')
	# plt.xlabel('Number of clusters')
	# plt.ylabel('Inertia')
	# plt.show()

	kmeans = KMeans(n_clusters=4)
	kmeans.fit(n_features_df[['total_section_count', 'n_time_between_groups', 'section_group_counts', 'section_all_group_counts']])
	cluster_labels = kmeans.labels_

	map_list_df['cluster'] = cluster_labels

	for i in range(4):
		map_ids = map_list_df[map_list_df['cluster'] == i].iloc[:4]['map_id'].values
		print(i, map_ids)
		for map_id in map_ids:
			groups_df = get_groups_df(map_id)
			visualize_all_groups(groups_df)
		plt.show()


