from tapping_data.groups_parsing import get_groups_df
from tapping_data.helpers import get_lists_path, get_map_ids_from_file_path, get_models_path
from tapping_data.sections_parsing import get_sections_dfs_dict, visualize_sections

import pandas as pd
import matplotlib.pyplot as plt

import os
import datetime
import time
import webbrowser

from gensim.models.doc2vec import Doc2Vec, TaggedDocument


def columns_to_word(row: pd.Series) -> str:
    """
    
    """
    if row.between_divisor == 4.0 and row.object_count_n == 16:
        return f"count_{str(row['object_count_n'])}_div_{str(row['between_divisor'])}_nextdiv_{str(row['next_divisor'])}"
    else:
        return 'placeholder'

def map_id_to_document(map_id: int) -> None:
    """
    
    """
    
    groups_df = get_groups_df(map_id)[['object_count_n', 'between_divisor', 'next_divisor']]
    #groups_df = groups_df[(groups_df.between_divisor == 4.0) & (groups_df.object_count_n == 16)].reset_index()

    groups_df['word'] = groups_df.apply(columns_to_word, axis=1)

    # print(map_id, words_columns['word'].values.tolist())
    return groups_df['word'].values.tolist()


def create_model(map_list_file: str = None) -> None:
    """
    
    """

    map_list_file_path = os.path.join(get_lists_path(), map_list_file)
    map_ids = get_map_ids_from_file_path(map_list_file_path)

    documents = []
    for map_id in map_ids:
        try:
            documents.append(TaggedDocument(words=map_id_to_document(map_id), tags=[str(map_id)]))
        except Exception as e:
            print(f'{map_id}: {e}')

    model = Doc2Vec(vector_size=32,   # Dimensionality of the document vectors
                    window=8,         # Maximum distance between the current and predicted word within a sentence
                    min_count=1,      # Ignores all words with total frequency lower than this
                    workers=4,        # Number of CPU cores to use for training
                    epochs=16,        # Number of training epochs
                    dm=1)        

    model.build_vocab(documents)
    model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
    
    file_name, _ = os.path.splitext(map_list_file)
    file_name = file_name + '_model'
    model.save(os.path.join(get_models_path(), file_name))


def get_similar_maps_doc2vec(map_id: int, map_list_file: str, top_n: int = 5) -> None:
    """
    
    """

    file_name, _ = os.path.splitext(map_list_file)
    file_name = file_name + '_model'
    model = Doc2Vec.load(os.path.join(get_models_path(), file_name))

    target_map_document = map_id_to_document(map_id)
    inferred_vector = model.infer_vector(target_map_document)
    most_similar_docs = model.dv.most_similar([inferred_vector], topn=top_n)
    for doc_id, similarity in most_similar_docs:
        print(f'Document ID: {doc_id}, Similarity: {similarity}') 

        groups_df = get_groups_df(doc_id)
        visualize_sections(groups_df)
		
        #webbrowser.open(f'https://osu.ppy.sh/b/{doc_id}')
        #time.sleep(0.5)
    groups_df = get_groups_df(map_id)
    visualize_sections(groups_df)
    plt.show()


