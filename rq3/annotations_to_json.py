import json
import sys
import pandas as pd


def annotations_to_json(csv):
    df = pd.read_csv(csv)
    d = {}
    for dataset in df['DatasetName'].unique():
        df_ = df[df['DatasetName'] == dataset]
        d[dataset] = {}
        for user in df_['UserID'].unique():
            d[dataset][str(user)] = [int(i) for i in
                df_[df_['UserID'] == user]['AnnotationIndex'] if i != 'no_cp']
    return d

if __name__ == "__main__":
    csv = sys.argv[1]
    d = annotations_to_json(csv)
    with open(csv.replace('.csv', '.json'), 'w') as f:
        json.dump(d, f)
