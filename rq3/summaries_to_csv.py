# Convert the JSON summaries to a CSV file.
import json
import os
import sys
import pandas as pd
from glob import glob

def read_summaries(base_dir, min_annotations=5):
    '''
    Read the JSON summaries from the given directory and return a dataframe
    with the summaries that have at least min_annotations annotations.
    '''
    summaries = []
    for filename in glob(os.path.join(base_dir, '*.json')):
        if os.path.getsize(filename) == 0:
            continue
        with open(filename) as f:
            summary = json.load(f)
        if len(summary['annotations']) >= min_annotations:
            summaries += get_params_and_scores(summary)

    return pd.DataFrame(summaries)

def get_params_and_scores(summary):
    '''
    Return a dictionary with the parameters and scores from the given summary.
    '''
    dataset = {}
    dataset['dataset'] = summary['dataset']
    dataset['n_datapoints'] = summary['dataset_nobs']
    dataset['n_annotations'] = len(summary['annotations'])

    scores_list = []
    for method, data in summary['results'].items():
        res = data[0]
        if res['status'] == 'FAIL':
            continue

        scores = dataset.copy()

        scores['method'] = method
        scores['f1'] = res['scores']['f1']
        scores['precision'] = res['scores']['precision']
        scores['recall'] = res['scores']['recall']
        scores['cover'] = res['scores']['cover']
        scores['parameters'] = dict_to_string(res['parameters'])
        scores['cplocations'] = list_to_string(res['cplocations'])

        scores_list.append(scores)

    return scores_list

def read_default_methods(from_file='default_methods.txt'):
    '''
    Read the default methods from the given file and return a list of them.
    '''
    with open(from_file) as f:
        return [line.strip() for line in f]

def set_default_methods(df):
    '''
    Set the default methods to the given dataframe.
    '''
    default_methods = read_default_methods()
    df['default'] = df['method'].isin(default_methods)
    return df

def dict_to_string(d):
    return json.dumps(d, separators=(',', ':'))

def list_to_string(l):
    return json.dumps(l)

def check_args():
    if len(sys.argv) != 2:
        print("Usage: python {} <summaries_dir>".format(sys.argv[0]))
        sys.exit(1)

if __name__ == "__main__":
    check_args()
    summaries_dir = sys.argv[1]

    df = read_summaries(summaries_dir)
    df = set_default_methods(df)
    df.to_csv('summaries.csv', index=False)
