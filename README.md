## osu-tapping-data
# Main features
- Parse objects of a beatmap into groups (doubles/triples, bursts, streams, etc)
- Create an embedding for each type of group (based on distances between the group's occurrences)
```py
# https://osu.ppy.sh/beatmapsets/39804#osu/129891 - Freedom Dive [FOUR DIMENSIONS]
from tapping_data.groups_ranking_parsing import get_groups_ranking_df

get_groups_ranking_df(map_id=129891,
                  between_divisor=4.0,
                  object_count_n=16,
                  update_entry=False)

   map_id            group_type  group_count                               ranking
0  129891  divisor_4.0_count_16           50  {'1': 2.5, '2': 3, '4': 2.0, '8': 0}
```
- Recommend similar maps based on a distance measure between embeddings
```py
# https://osu.ppy.sh/beatmapsets/39804#osu/129891 - Freedom Dive [FOUR DIMENSIONS]
from tapping_data.groups_ranking_utility import compute_rank_distance, get_similar_maps_by_rank_distance

get_similar_maps_by_rank_distance(map_list_file,
                              target_map_id=129891,
                              target_between_divisor=4.0,
                              target_object_count_n=16,
                              top_n=8,
                              visualize=False,
                              open_links=False)

       map_id            group_type  group_count                                   ranking  distance
4324   889228  divisor_4.0_count_16           32  {'1': 2.5, '2': 3.0, '4': 2.0, '8': 0.0}       0.0
1387   555797  divisor_4.0_count_16           49  {'1': 2.5, '2': 3.0, '4': 2.0, '8': 0.0}       0.0
2055  1488097  divisor_4.0_count_16           26  {'1': 3.0, '2': 3.0, '4': 2.0, '8': 0.0}       0.5
4313   495776  divisor_4.0_count_16           27  {'1': 3.0, '2': 3.0, '4': 2.0, '8': 0.0}       0.5
3316  1256809  divisor_4.0_count_16           48  {'1': 3.0, '2': 3.0, '4': 2.0, '8': 0.0}       0.5
...       ...                   ...          ...                                       ...       ...
5075   908042  divisor_4.0_count_16           27  {'1': 3.0, '2': 1.0, '4': 3.0, '8': 0.0}       3.5
1975  1617365  divisor_4.0_count_16           26  {'1': 3.0, '2': 0.5, '4': 2.5, '8': 0.5}       4.0
2319  1101611  divisor_4.0_count_16           39  {'1': 2.5, '2': 0.0, '4': 3.0, '8': 1.0}       5.0
2249   837567  divisor_4.0_count_16           39  {'1': 3.0, '2': 0.0, '4': 1.5, '8': 1.5}       5.5
2642  1241370  divisor_4.0_count_16           48  {'1': 3.0, '2': 0.0, '4': 1.0, '8': 2.0}       6.5

[112 rows x 5 columns]
```
## 1. Parse any osu!std beatmap into an objects dataframe 
```py
# https://osu.ppy.sh/beatmapsets/39804#osu/129891 - Freedom Dive [FOUR DIMENSIONS]
from tapping_data.objects_parsing import get_objects_df

objects_df = get_objects_df(map_id=129891)
print(objects_df)

      start_time  end_time  beat_length  time_next_object
0           2133      2538   270.002686        540.005371   # slider/spinner
1           2673      2674   270.002686        135.001343   # circle
2           2808      2809   270.002686        135.001343
3           2943      3078   270.002686        270.002686
4           3213      3618   270.002686        540.005371
...          ...       ...          ...               ...
1978      256813    256814   270.002686         67.500671
1979      256880    256881   270.002686         67.500671
1980      256948    256949   270.002686         67.500671
1981      257015    257016   270.002686         67.500671
1982      257083    261335   270.002686          0.000000

[1983 rows x 4 columns]
```
#### Meaning of *objects_df* columns:
- `start_time` - millisecond offset in the song/map when the object is supposed to be clicked
- `end_time` - millisecond offset in the song/map when the object is supposed to be let go of
- `beat_length` - milliseconds in a full beat of the bpm of the object (bpm = 60000 / beat_length)
- `time_next_object` - milliseconds from this object's `start_time` until the next object's `start_time`
   
## 2. Parse objects into groups (doubles/triples, bursts, streams) 
```py
# https://osu.ppy.sh/beatmapsets/39804#osu/129891 - Freedom Dive [FOUR DIMENSIONS]
from tapping_data.groups_parsing import get_groups_df

groups_df = get_groups_df(map_id=129891)
print(groups_df)

     start_time  end_time  beat_length  time_between_objects  time_next_group  object_count  object_count_n  between_divisor  next_divisor
0          2133      2133   270.002686            540.005371       540.005371             1               4              0.5           0.5    
1          2673      2943   270.002686            135.001343       270.002686             3               4              2.0           1.0
2          3213      3213   270.002686            540.005371       540.005371             1               4              0.5           0.5    
3          3753      4023   270.002686            135.001343       270.002686             3               4              2.0           1.0    
4          4293      4293   270.002686            540.005371       540.005371             1               4              0.5           0.5    
..          ...       ...          ...                   ...              ...           ...             ...              ...           ...    
332      249320    249455   270.002686            135.001343       270.002686             2               4              2.0           1.0    
333      249725    249995   270.002686            270.002686       270.002686             2               4              1.0           1.0    
334      250265    250400   270.002686            135.001343       135.001343             2               4              2.0           2.0    
335      250535    252560   270.002686             67.500671       135.001343            31              16              4.0           2.0    
336      252695    257083   270.002686             67.500671         0.000000            66              16              4.0           0.0    

[337 rows x 9 columns]
```
#### Meaning of *groups_df* columns:
- `start_time` - millisecond offset in the song/map when the group starts
- `end_time` - millisecond offset in the song/map when the group ends
- `beat_length` - milliseconds in a full beat of the bpm of the group (bpm = 60000 / beat_length)
- `time_between_objects` - milliseconds between the objects of the group
- `time_next_group` - milliseconds from the end of this group until the first object of the next group
- `object_count` - number of objects in the group
- `object_count_n` - normalized value of object_count (between 1-4 normalize to 4, 5-8 normalize to 8, 9+ normalize to 16)
- `between_divisor` - time_between_objects / beat_length
- `next_divisor` - time_next_group / beat_length

# Future work
  - fix maps with lots of bpm changes
  - simpler embedding (remove the black magic code for breaks within 10% of each other)
  - other distance measure between embeddings such as total rank distance
  - experiment with other ranking embeddings, for example count of each type of group (such as count of all 1/4 and 1/2 groupings)
  - better/actual tests
    
# Credits
  - osu_analysis by abraker, used for parsing raw beatmap files: https://github.com/abraker-osu/osu_analysis 
