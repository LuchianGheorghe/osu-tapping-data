import pytest
import os
from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df
from tapping_data.helpers import get_parsed_maps_path


@pytest.fixture(scope="module")
def prepare_objects_df():
    return get_objects_df(373410, update_entry=True)

# add all split groups, check if count matches original groups_df row count

# check if every pair of (between_divisor, object_count_n) has a similar_group