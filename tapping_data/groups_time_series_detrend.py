from tapping_data.groups_parsing import get_groups_df
from tapping_data.sections_parsing import get_sections_dfs_dict, visualize_sections

import matplotlib.pyplot as plt



def groups_time_series_detrend(map_id: str) -> None:
	"""
	
	"""

	groups_df = get_groups_df(map_id)

	start_times = groups_df.loc[
		(groups_df['between_divisor'] == 4.0) &
		(groups_df['object_count_n'] == 16)
	]['start_time'].values

	detrend_start_times = []
	for i in range(1, len(start_times)):
		detrend_start_times.append(
			start_times[i] - start_times[i - 1]
		)

	inverse_detrend_start_times = []
	for val in detrend_start_times:
		inverse_detrend_start_times.append((1 / val))

	print(start_times)
	print(detrend_start_times)
	print(inverse_detrend_start_times)

	visualize_sections(groups_df)
	plt.show()
	start_times = start_times[1:]

	#plt.plot(start_times)
	#plt.plot(detrend_start_times)
	plt.plot(start_times, inverse_detrend_start_times)
