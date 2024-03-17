from tapping_data.context_sections_parsing import get_all_context_sections_stats_dict
from tapping_data.sections_statistics import get_sections_stats_dict
from tapping_data.sections_parsing import get_sections_dfs_dict, visualize_sections
from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df
from tapping_data.helpers import get_map_ids_from_file_path, get_lists_path, create_empty_series

from tapping_data.vectorize_attempt import get_map_list_section_stats_df

from beatmap_reader import BeatmapIO
import os

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import time


def context_sections(map_id):
	groups_df = get_groups_df(map_id, update_entry=True)

	all_context_sections_stats_dict = get_all_context_sections_stats_dict(groups_df)
	for section in all_context_sections_stats_dict:
		print(section)
		for subsection in all_context_sections_stats_dict[section]:
			print(f'\t{subsection}: {all_context_sections_stats_dict[section][subsection]}')

	visualize_sections(groups_df)


def find_closest_map_ids_primary(given_map_id, df, top_n=25):
	if given_map_id not in df['map_id'].values:
		print("Target map_id not found in the dataframe")
		return

	features_df = df.drop(['map_id'], axis=1)
	normalized_features = features_df - features_df.mean()
	given_index = df.index[df['map_id'] == given_map_id].tolist()[0]

	similarities = cosine_similarity([normalized_features.iloc[given_index]], normalized_features)[0]

	closest_indices = np.argsort(-similarities)[:top_n + 1]
	closest_map_ids = df['map_id'].iloc[closest_indices].values

	return closest_map_ids


def find_closest_map_ids_secondary(target_map_id, closest_map_ids_primary, df, top_n=10):
	if target_map_id not in df['map_id'].values:
		print("Target map_id not found in the dataframe")
		return

	df_closest_map_ids_primary = df.loc[df['map_id'].isin(closest_map_ids_primary)].reset_index()
	
	target_index = df_closest_map_ids_primary.index[df_closest_map_ids_primary['map_id'] == target_map_id].tolist()[0]
	
	features_df = df_closest_map_ids_primary.drop('map_id', axis=1)
	normalized_features = features_df - features_df.mean()

	similarities = cosine_similarity([normalized_features.iloc[target_index]], normalized_features)[0]

	closest_indices = np.argsort(-similarities)[:top_n + 1]
	closest_map_ids = df_closest_map_ids_primary['map_id'].iloc[closest_indices].values

	return closest_map_ids


def main(*map_ids, map_list_file=None):
	if map_list_file:
		target_map_id = 345099
		target_section_primary = 'divisor_2.0'
		target_section_secondary = 'divisor_4.0'
		
		map_list_section_stats_df_primary = get_map_list_section_stats_df(map_list_file, target_section_primary, update_entry=False)
		map_list_section_stats_df_secondary = get_map_list_section_stats_df(map_list_file, target_section_secondary, update_entry=False)
		# print(map_list_section_stats_df)
		
		closest_map_ids_primary = find_closest_map_ids_primary(target_map_id, map_list_section_stats_df_primary, 25)
		print(closest_map_ids_primary)

		closest_map_ids_secondary = find_closest_map_ids_secondary(target_map_id, closest_map_ids_primary, map_list_section_stats_df_secondary)
		print(closest_map_ids_secondary)

		for map_id in closest_map_ids_secondary:
			groups_df = get_groups_df(map_id)
			sections_stats_dict = get_sections_stats_dict(get_sections_dfs_dict(groups_df))
			visualize_sections(groups_df)
			matching_sections = [existing_section for existing_section in sections_stats_dict if target_section_primary in existing_section or target_section_secondary in existing_section]
			for section in matching_sections:
				print(map_id, section, sections_stats_dict[section])
			print()
		
		for map_id in closest_map_ids_secondary:
			webbrowser.open(f'https://osu.ppy.sh/b/{map_id}')
			time.sleep(0.2)

		plt.show()

	else:
		for map_id in map_ids:
			# context_sections(map_id)
			for map_id in map_ids:
				groups_df = get_groups_df(map_id)
				sections_stats_dict = get_sections_stats_dict(get_sections_dfs_dict(groups_df))
				visualize_sections(groups_df)
				print(map_id)
				for section in sections_stats_dict:
					print(f'\t{section}: {sections_stats_dict[section]}')
			plt.show()


if __name__ == '__main__':
	try:
		main(map_list_file='tourney_maps_list.txt')
		#main(2097288)
	except ValueError as invalid_id:
		print(invalid_id)
	except BeatmapIO.BeatmapIOException as non_std_gamemode:
		print(non_std_gamemode)

	# main(345099, 315354, 435350, 255694)  # natsu airman, sparkling daydream, choir jail, fantastic future
	# main(918415, 898597, 1845874)  # feelin sky
	# main(221777, 776951)
	# main(2983479, 3665005)  # lion heart vs glory days
	# main(574471, 955864, 290581, 516322)  # best friends vs m flat vs diamond vs love sick
	# main(668662, 2082018, 252236)  # ice angel vs blend s vs stream2
	# main(776951, 2850905)  # night of knights vs chained girl
	# main(776951, 2850905, 1839789)  # night of knights vs chained girl vs gid v
	# main(351752, 429989)  # view of river styx RLC vs GoldenWolf
	# main(221777, 260489)  # pretender vs near distant future
	# main(129891, 658127)  # freedom dive vs blue zenith
	# main(1764213) # harumachi clover sotarks
	# main(221777) # pretender
	# main(260489) # near distant future
	# main(734927) # the_relentless
	# main(340652) # pi li pa la
	# main(1906932) # bohemian rhapsody
	# main(351752) # view of river styx RLC
	# main(429989) # view of river styx GoldenWolf
	# main(2719326) # sputnik
	# main(161787) # dmc
	# main(2101986) # i thought i was an angel
	# main(792420) # throw away
	# main(952010) # eclipse parade
	# main(1193177) # neuro-cloud-9
	# main(768454) # brazil easter
	# main(847314) # tower of heaven
	# main(817155) # transcend chillout
	# main(292574) # cheatreal square practice
	# main(915058) # soukai rock ely
	# main(772293) # sewing machine
	# main(2708952) # xenobeat
	# main(668662) # ice angel
	# main(129891) # freedom dive
	# main(658127) # blue zenith
	# main(3435049) # Celina & TD's Collab Extra
	# main(776951) # night of knights alacat
	# main(252236) # stream2
	# main(2082018) # blendS barkingmaddog
	# main(1529189) # painters of the tempest
	# main(574471) # best friends
	# main(955864) # m flat
	# main(1839789)  # Gid V
	# main(726357)  # mirage garden charles
	# main(1644000)  # Alice in Misanthrope -Ensei Alice-
	# main(907479)  # true blue
	# main(1682424)  # what you do blue dragon
	# main(2983479) # lion heart
	# main(3665005) # glory days
	# main(516322) # love sick
	# main(3261335) # carless claris - 1/3s
	# main(252238) # image material
	# main(path='test.txt') 