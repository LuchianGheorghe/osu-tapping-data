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


def columns_to_word(row: pd.Series) -> str:
    """
    
    """

    if row['object_count_n'] == 16 and row['between_divisor'] == 4.0:
        return f"count_{str(row['object_count_n'])}_div_{str(row['between_divisor'])}_nextdiv_{str(row['next_divisor'])}"
    else:
        if row['next_divisor'] == 1000.0:
            return f"placeholder_{str(row['next_divisor'])}"
        else:
            return 'placeholder'


def map_id_to_document_all_groups(map_id: int, section: str) -> None:
    """
    
    """

    groups_df = get_groups_df(map_id)[['object_count_n', 'between_divisor', 'next_divisor']]
    groups_df['word'] = groups_df.apply(columns_to_word, axis=1)

    # print(map_id, words_columns['word'].values.tolist())
    return groups_df['word'].values.tolist()


def map_id_to_document_context_sections(map_id: int, section: str) -> None:
    """
    
    """
    
    groups_df = get_groups_df(map_id)
    sections_dfs_dict = get_sections_dfs_dict(groups_df)
    try:
        split_context_sections_dfs = get_split_context_sections_dfs(groups_df, sections_dfs_dict, section)
    except Exception as e:
        raise e

    context_sections_df = pd.DataFrame(columns=['object_count_n', 'between_divisor', 'next_divisor'])
    context_sections_df['object_count_n'] = context_sections_df['object_count_n'].astype('int16')
    context_sections_df['between_divisor'] = context_sections_df['between_divisor'].astype('float32')
    context_sections_df['next_divisor'] = context_sections_df['next_divisor'].astype('float32')

    for split_df in split_context_sections_dfs:
        split_df_concat = split_df[['object_count_n', 'between_divisor', 'next_divisor']]
        split_df_concat.loc[split_df_concat.index[-1], 'next_divisor'] = 1000.0
        context_sections_df = pd.concat([context_sections_df, split_df_concat], ignore_index=True)

    context_sections_df['word'] = context_sections_df.apply(columns_to_word, axis=1)

    # print(map_id, words_columns['word'].values.tolist())
    return context_sections_df['word'].values.tolist()


def create_model(map_list_file: str, section: str, map_id_to_document: Callable = map_id_to_document_all_groups) -> None:
    """
    
    """

    file_name, _ = os.path.splitext(map_list_file)
    documents_file = os.path.join(get_models_path(), file_name + '_documents')

    if os.path.exists(documents_file):
        with open(documents_file, 'rb') as f:
            documents = pickle.load(f)
    else:
        map_list_file_path = os.path.join(get_lists_path(), map_list_file)
        map_ids = get_map_ids_from_file_path(map_list_file_path)

        documents = []
        for map_id in map_ids:
            try:
                documents.append(TaggedDocument(words=map_id_to_document(map_id, section), tags=[str(map_id)]))
            except Exception as e:
                print(f'{map_id}: {e}')

        with open(documents_file, 'wb') as f:
            pickle.dump(documents, f)

    model = Doc2Vec(vector_size=32,   # Dimensionality of the document vectors
                    window=16,         # Maximum distance between the current and predicted word within a sentence
                    min_count=1,      # Ignores all words with total frequency lower than this
                    workers=4,        # Number of CPU cores to use for training
                    epochs=128,        # Number of training epochs
                    dm=1)        

    model.build_vocab(documents)
    model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
    
    file_name, _ = os.path.splitext(map_list_file)
    file_name = file_name + '_model'
    model.save(os.path.join(get_models_path(), file_name))


def get_similar_maps_doc2vec(map_id: int, map_list_file: str, section: str, top_n: int = 5, map_id_to_document: Callable = map_id_to_document_all_groups) -> None:
    """
    
    """

    file_name, _ = os.path.splitext(map_list_file)
    file_name = file_name + '_model'
    model = Doc2Vec.load(os.path.join(get_models_path(), file_name))

    target_map_document = map_id_to_document(map_id, section)
    inferred_vector = model.infer_vector(target_map_document)
    most_similar_docs = model.dv.most_similar([inferred_vector], topn=top_n)
    for doc_id, similarity in most_similar_docs:
        print(f'Document ID: {doc_id}, Similarity: {similarity}') 

        groups_df = get_groups_df(doc_id)
        visualize_sections(groups_df)
		
        webbrowser.open(f'https://osu.ppy.sh/b/{doc_id}')
        time.sleep(0.5)
    groups_df = get_groups_df(map_id)
    visualize_sections(groups_df)
    plt.show()


