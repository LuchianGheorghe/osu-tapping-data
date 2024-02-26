import pytest
import os
from tapping_data.objects_parsing import get_objects_df
from tapping_data.helpers import get_downloaded_maps_path, get_parsed_maps_path


@pytest.fixture(scope="module")
def prepare_objects_df():
    return get_objects_df(373410, update_entry=True)


def test_downloaded_path_exists(prepare_objects_df):
    downloaded_path = os.path.join(get_downloaded_maps_path(), '373410.osu')
    assert os.path.exists(downloaded_path) == True


def test_parsed_objects_path_exists(prepare_objects_df):
    parsed_objects_path = os.path.join(get_parsed_maps_path(), '373410_objects')
    assert os.path.exists(parsed_objects_path) == True


def test_objects_df_length(prepare_objects_df):
    objects_df = prepare_objects_df
    assert len(objects_df) == 267


def test_objects_df_end_time(prepare_objects_df):
    objects_df = prepare_objects_df
    assert objects_df.iloc[-1].end_time == 95437