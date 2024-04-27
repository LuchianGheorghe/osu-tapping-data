from tapping_data.groups_parsing import visualize_select_group
from tapping_data.groups_rank_distance import get_rankings_df, compute_rank_distance

from random import sample
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from scipy.cluster import hierarchy


def get_distance_matrix(rankings_df: pd.DataFrame) -> np.ndarray:
    """
    
    """

    n_samples = rankings_df.shape[0]

    distance_matrix = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            ranking_i = rankings_df.iloc[i]['ranking']
            ranking_j = rankings_df.iloc[j]['ranking']
            distance_matrix[i, j] = distance_matrix[j, i] = compute_rank_distance(ranking_i, ranking_j)

    return distance_matrix


def plot_dendrogram(model, **kwargs):
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)

    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    hierarchy.dendrogram(linkage_matrix, **kwargs)


def test_distances(distance_matrix):
    for distance_threshold in range(1, 18):
        distance_threshold /= 2
        
        clustering = AgglomerativeClustering(n_clusters=None, metric='precomputed', linkage='average', compute_full_tree=True, distance_threshold=distance_threshold)
        clustering.fit_predict(distance_matrix)

        silh_score = silhouette_score(distance_matrix, clustering.labels_)
        db_index = davies_bouldin_score(distance_matrix, clustering.labels_)
        ch_score = calinski_harabasz_score(distance_matrix, clustering.labels_)

        print(f'{distance_threshold=}, {clustering.n_clusters_=}')
        print(Counter(clustering.labels_))
        print("Silhouette Score: ", silh_score)
        print("Davies-Bouldin Index: ", db_index)
        print("Calinski-Harabasz Index: ", ch_score)
        print()


def sklearn_agglomerative_clustering(map_list_file: str, between_divisor: float, object_count_n: float):
    """
    
    """

    rankings_df = get_rankings_df(map_list_file, between_divisor, object_count_n, update_entry=False)
    distance_matrix = get_distance_matrix(rankings_df)

    print(rankings_df.loc[rankings_df.map_id == 2893329])

    # test_distances(distance_matrix)
    # return

    distance_threshold = 0.5

    clustering = AgglomerativeClustering(n_clusters=None, metric='precomputed', linkage='average', compute_full_tree=True, distance_threshold=distance_threshold)
    clustering.fit_predict(distance_matrix)

    print(f'{len(clustering.labels_)=}')
    print(Counter(clustering.labels_))
    
    plot_dendrogram(clustering, truncate_mode="level", p=5)
    plt.axhline(y=distance_threshold, c='k', ls='--', lw=0.8, label=f'Cut at distance = {distance_threshold}')
    plt.show()

    rankings_df['cluster'] = clustering.labels_

    target_map_id = 817155
    target_cluster = rankings_df.loc[rankings_df['map_id'] == target_map_id]['cluster'].values[0]
    print(f'{target_map_id=}, {target_cluster=}')
    
    map_ids = rankings_df.loc[rankings_df['cluster'] == 3]['map_id'].values.tolist()
    map_ids_sample = sample(map_ids, 5)

    for map_id in map_ids_sample:
        visualize_select_group(map_id, between_divisor, object_count_n)
    plt.show()


def driver(map_list_file: str, between_divisor: float, object_count_n: float):
    """
    
    """

    sklearn_agglomerative_clustering(map_list_file, between_divisor, object_count_n)
