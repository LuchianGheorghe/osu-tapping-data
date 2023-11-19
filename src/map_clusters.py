import os, math
import pandas as pd
import matplotlib.pyplot as plt
from map_groups import get_groups_df
from helper import print_t, get_data_path, round_divisor, create_empty_series


def cast_types(clusters_df):
    return clusters_df


def EM(data_points):
    from sklearn.mixture import GaussianMixture
    from scipy.stats import norm
    import numpy as np

    data = np.array(data_points).reshape(-1, 1)
    print(data_points)
    print()
    
    n_components = np.arange(1, 10)
    models = [GaussianMixture(n, covariance_type='full', random_state=0).fit(data) for n in n_components]
    
    for model in models:
        means = model.means_.flatten()
        covariances = model.covariances_.flatten()
        weights = model.weights_.flatten()
        aic = model.aic(data)
        #print(means, covariances, weights, aic)
        print(aic)

    colors = ['blue', 'green', 'orange', 'black', 'pink', 'brown', 'red']

    # Plot each Gaussian component of the best model
    best_gmm = models[4]
    x_dense = np.linspace(min(data_points) - 50000, max(data_points) + 50000, 10000)
    densities = np.exp(best_gmm.score_samples(x_dense.reshape(-1, 1)))

    plt.figure(figsize=(10, 6))

    for i, (mean, cov, weight) in enumerate(zip(best_gmm.means_.flatten(), best_gmm.covariances_.flatten(), best_gmm.weights_.flatten())):
        component_density = weight * norm.pdf(x_dense, mean, np.sqrt(cov))
        plt.plot(x_dense, component_density, label=f'Component {i+1}', color=colors[i])
        plt.axvline(x=mean, color=colors[i], linestyle='--', label=f'Mean {i+1}: {mean:.2f}')

    # Plot the data points on the x-axis
    plt.scatter(data_points, np.zeros_like(data_points), color='red', s=30, label='Data Points')

    # Add labels and legend
    plt.title('Gaussian Components and Data Points')
    plt.xlabel('Data Points')
    plt.ylabel('Probability Density')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    # Adjust the y-axis to better visualize the Gaussian components
    plt.ylim(bottom=0, top=max(densities) + 0.05 * max(densities))

    # Show the plot
    plt.show()

    #aics = [m.aic(data) for m in models]
    #bics = [m.bic(data) for m in models]

    #return (n_components, aics, bics)


def parse_clusters(map_id, map_strain_csv):
    groups_df = get_groups_df(map_id, update_entry=True)
    groups_df_sorted = groups_df.sort_values(by=['between_divisor', 'object_count_n'], ascending=False).reset_index(drop=True)

    similar_groups = []
    new_similar = []
    for i, curr_row in groups_df_sorted.iterrows():
        if len(new_similar) == 0: 
            new_similar.append(curr_row)

        if i == groups_df_sorted.shape[0] - 1:
            similar_groups.append(new_similar)
            break

        next_row = groups_df_sorted.iloc[i+1]
        if next_row['between_divisor'] == curr_row['between_divisor'] and next_row['object_count_n'] == curr_row['object_count_n']:
            new_similar.append(next_row)
        else:
            similar_groups.append(new_similar)
            new_similar = []

    data_points = []
    for row in similar_groups[2]:
        data_points.append(row['start_time'])
    EM(data_points)

    map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df['start_time'], groups_df['between_divisor'], groups_df['object_count_n'], c=groups_df['between_divisor'], cmap='Accent')
    plt.colorbar(map_plot)
    sorted_map_plot = plt.figure().add_subplot(111, projection='3d').scatter(groups_df_sorted.index, groups_df_sorted['between_divisor'], groups_df_sorted['object_count_n'], c=groups_df_sorted['between_divisor'], cmap='Accent')
    plt.colorbar(sorted_map_plot)
    plt.show()

    # columns = ['start_time', 'end_time', 'beat_length', 'object_count_n', 'between_divisor', 'group_count', 'time_between_groups']
    # clusters_df = pd.DataFrame(columns=columns)
    # new_cluster = create_empty_series(columns)


    '''
    for idx, cur_row in groups_df_sorted.iterrows():
        if idx == groups_df_sorted.shape[0] - 1:
            #todo
            break

        next_row = groups_df_sorted.iloc[idx + 1]
    
        if next_row['between_divisor'] == cur_row['between_divisor'] and next_row['object_count_n'] == cur_row['object_count_n']:
            time_next_cluster = next_row['start_time'] - cur_row['start_time']
            if new_cluster.group_count is None:
                new_cluster.time_between_groups = time_next_cluster
                new_cluster.group_count = 1
            else:
                # todo: think of a better value for minimum distance between groups of a cluster
                if abs(new_cluster.time_between_groups - time_next_cluster) <= new_cluster.time_between_groups / 4:
                    new_cluster.group_count += 1
                    continue
                if new_cluster.time_between_groups > time_next_cluster:
                    clusters_df = pd.concat([clusters_df, new_cluster.to_frame().T], ignore_index=True)
                    new_cluster = create_empty_series(columns)
                    new_cluster.time_between_groups = time_next_cluster
                    new_cluster.group_count = 1
                else:
                    new_cluster.group_count += 1
                    clusters_df = pd.concat([clusters_df, new_cluster.to_frame().T], ignore_index=True)
                    new_cluster = create_empty_series(columns)
        else:
            new_cluster.group_count = 1 if new_cluster.group_count is None else new_cluster.group_count + 1
            clusters_df = pd.concat([clusters_df, new_cluster.to_frame().T], ignore_index=True)
            new_cluster = create_empty_series(columns)
    '''
    # return clusters_df


def get_clusters_df(map_id, update_entry=False):
    map_clusters_file = os.path.join(get_data_path(), str(map_id) + '_clusters')
    # if not os.path.exists(map_chunks_file):
        # parse_strain(map_id, map_chunks_file)
    return parse_clusters(map_id, map_clusters_file)
    #return pd.read_parquet(map_chunks_file)


