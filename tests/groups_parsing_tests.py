import pytest
import os
from tapping_data.objects_parsing import get_objects_df
from tapping_data.groups_parsing import get_groups_df
from tapping_data.helpers import get_parsed_maps_path


@pytest.fixture(scope="module")
def prepare_objects_df():
    return get_objects_df(373410, update_entry=True)


@pytest.fixture(scope="module")
def prepare_groups_df():
    return get_groups_df(373410, update_entry=True)


def test_parsed_groups_path_exists(prepare_groups_df):
    parsed_path = os.path.join(get_parsed_maps_path(), '373410_groups')
    assert os.path.exists(parsed_path) == True


def test_group_object_count_sum(prepare_objects_df, prepare_groups_df):
    objects_df = prepare_objects_df
    groups_df = prepare_groups_df
    assert len(objects_df) == groups_df['object_count'].sum()