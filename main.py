from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df, visualize_all_groups, visualize_select_group
from tapping_data.helpers import get_map_ids_from_file_path, get_lists_path, create_empty_series, round_divisor
from tapping_data.groups_ranking_utility import compute_rank_distance, get_similar_maps_by_rank_distance
from tapping_data.groups_ranking_parsing import get_groups_ranking_df, get_groups_rankings_list_df, map_id_to_ranking

from beatmap_reader import BeatmapIO
import matplotlib.pyplot as plt


def main(*map_ids, map_list_file=None):
	if map_list_file:
		groups_rankings_list_df = get_groups_rankings_list_df(map_list_file, between_divisor=4.0, object_count_n=16, update_entry=False)
		print(groups_rankings_list_df)
		
		# get_similar_maps_by_rank_distance(map_list_file, target_map_id=129891, target_between_divisor=4.0, target_object_count_n=16, top_n=8, visualize=False, open_links=False)
	else:
		for map_id in map_ids:
			groups_ranking_df = get_groups_ranking_df(map_id, between_divisor=4.0, object_count_n=16, update_entry=False)
			print(groups_ranking_df)

import pandas as pd
if __name__ == '__main__':
	try:
		# print(map_id_to_ranking(129891, 4.0, 16))
		# visualize_sections(get_groups_df(1521481))
		# plt.show()
		main(map_list_file='all_maps_2015-2018.txt')
		# main(129891)
		# from tapping_data.groups_parsing import visualize_all_groups, visualize_select_group
		# visualize_all_groups(129891)
		# visualize_select_group(visualize_all_groups, between_divisor=4, object_count_n=16)
		# get_groups_df(129891)
		# print(get_groups_df(1257904, update_entry=True))
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
	# main(550235) # united
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
 