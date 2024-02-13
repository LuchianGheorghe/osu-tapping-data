import time
import pandas as pd
import matplotlib.pyplot as plt	
from sqlalchemy import create_engine, text
from helper import get_map_ids_from_file, round_divisor, print_t
from map_chunks import get_chunks_df
from map_categories import get_categories_df, get_categories_df_n
from map_objects import get_objects_df, get_beatmap_data
from map_info import get_map_info_df
from map_strain import get_strain_df
from map_groups import get_groups_df
from map_clusters import get_clusters_df
from db_manager import init_db, add_maps_to_db, read_maps_from_db, read_maps_info_from_db
from osu_db import MapsDB

from beatmap_reader import BeatmapIO


def test(value, modifier):
	result = value + value / modifier
	if result < 0:
		return 0
	return result


def get_similar_condition_ids(df, map_id, divisor, columns):
	map_df = df.loc[(df.map_id == map_id) & (df.divisor == divisor)]
	columns_values_dict = {}
	for _, row in map_df.iterrows():
		columns_values_dict = row[columns].to_dict()
	columns_values_dict = dict(sorted(columns_values_dict.items(), key=lambda x: x[1], reverse=True))

	conditions = []
	for column, value in columns_values_dict.items():
		conditions.append(df[column].between(test(value, -2), test(value, 2)))

	final_condition = df.divisor == divisor
	for condition in conditions:
		final_condition = final_condition & condition

	return set(df.loc[final_condition].map_id.to_list())


def main(*map_ids, path=None):
	for map_id in map_ids:
		get_clusters_df(map_id, update_entry=True)
		print()
	
	#df = df.drop(labels=['time_between_objects', 'time_next_group', 'next_divisor', 'beat_length'], axis=1)

	#map_plot = plt.figure().add_subplot(111, projection='3d').scatter(df['start_time'], df['between_divisor'], df['object_count_n'], c=df['between_divisor'], cmap='Accent')
	#plt.colorbar(map_plot)

	#df = df.sort_values(by=['between_divisor', 'object_count_n'], ascending=False).reset_index(drop=True)
	#print(df)

	# plt.scatter(df.index, df['object_count_n'], c=df['between_divisor'], cmap='Accent')
	# plt.xlabel('start_time')
	# plt.ylabel('object_count')
	# plt.title('Scatter Plot Colored by between_divisor')
	# plt.colorbar()

	# sorted_map_plot = plt.figure().add_subplot(111, projection='3d').scatter(df.index, df['between_divisor'], df['object_count_n'], c=df['between_divisor'], cmap='Accent')
	# plt.colorbar(sorted_map_plot)
	
	# plt.show()

    # if path:
    # 	map_ids = get_map_ids_from_file(path)

    # if map_ids != ():
    # 	init_db(recreate_db=False)
    # 	add_maps_to_db(map_ids, update_entry=False)

    # df = read_maps_from_db()

    # for map_id in map_ids: 
    # 	print(df.loc[df.map_id == map_id])
	

if __name__ == '__main__':
	try:
		main(351752, 429989)
	except ValueError as invalid_id:
		print(invalid_id)
	except BeatmapIO.BeatmapIOException as non_std_gamemode:
		print(non_std_gamemode)

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
	# main(path='test.txt') 

	'''
		# print(df.sort_values('finger_control_groups', ascending=False))

	# strain_df = get_strain_df(3106044)
	# strain_df[['local_strain', 'perceived_strain']].plot()
	# plt.show()

	# map_id = 2105741
	# print(df.loc[df.map_id == map_id])

	# similar_div2_total_strain_ids = get_similar_condition_ids(df, map_id, 2, ['stream_strain', 'burst_strain'])
	# similar_div4_category_groups_ids = get_similar_condition_ids(df, map_id, 4, ['total_strain'])
	# conditions_intersection = list(set.intersection(similar_div2_total_strain_ids, similar_div4_category_groups_ids))

	# similar_maps_df = df.loc[(df.map_id.isin(similar_div4_category_groups_ids)) & (df.divisor == 4)] \
	# similar_maps_df = df.loc[(df.divisor == 4)] \
	# 				.sort_values(['stream_strain', 'burst_strain']) \
	# 				.reset_index(drop=True)
	# index = similar_maps_df.loc[similar_maps_df.map_id == map_id].index.values[0]
	# similar_maps_df = similar_maps_df.iloc[index - 3 : index + 4].copy()
	# similar_maps_ids = similar_maps_df.map_id.to_list()

	# for similar_map_id in similar_maps_ids:
	# 	print(df[df['map_id'] == similar_map_id].sort_values('divisor', ascending=False))
	# 	print()

	# import webbrowser
	# for similar_map_id in similar_maps_ids:
	# 	webbrowser.open(f'https://osu.ppy.sh/b/{similar_map_id}')
	# 	time.sleep(0.2)

	# print(df.loc[df.divisor == 4].sort_values('stream_groups', ascending=False).head(25))

	# for map_id in []:
	# 	strain_df = get_strain_df(map_id, update_entry=True)
	# 	categories_df = get_categories_df_n(map_id, strain_type='perceived_strain')
	# 	print(categories_df)
	# 	print()
	'''