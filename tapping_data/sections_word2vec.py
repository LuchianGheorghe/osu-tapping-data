from tapping_data.groups_parsing import get_groups_df
from tapping_data.helpers import get_lists_path, get_map_ids_from_file_path, get_models_path
from tapping_data.sections_parsing import get_sections_dfs_dict, visualize_sections
from tapping_data.context_sections_parsing import get_split_context_sections_dfs

import pandas as pd
import matplotlib.pyplot as plt

import os
import datetime
import time
import webbrowser
from typing import Callable
import pickle

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models.word2vec import Word2Vec


def test() -> None:
    map_id = 772293

    groups_df = get_groups_df(map_id)
    print(groups_df.to_string())

