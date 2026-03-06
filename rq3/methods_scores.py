import sys
import pandas as pd

SCORES = ['precision', 'recall', 'f1']

DATASETS = {
    'GraalVM': 'graal',
    'MongoDB': 'mongodb',
    'SAP HANA' : 'sap',
}

def compute_default_scores(df):
    df = df[df['default'] == True]
    scores = df.groupby(['method_name'])[SCORES].mean()
    return scores

def average_highest_score(df, metric):
    """
    In the Oracle experiment, the score is the average of
    the highest score obtained for each series.
    """
    if metric in ['precision', 'recall']:
        # When getting the Oracle for Precision and Recall,
        # we only present the ones associated with the Highest average F1
        df = df[df['f1'] == df.groupby(['dataset', 'method_name'])['f1'].transform('max')]
    df = df[df[metric] == df.groupby(['dataset', 'method_name'])[metric].transform('max')]
    return df.groupby(['method_name'])[metric].mean()

def compute_best_scores(df):
    scores = [average_highest_score(df, metric) for metric in SCORES]
    return pd.DataFrame(scores).T

def scores_to_latex(dataset, default_scores, best_scores):

    # Build the latex template for the table
    header = r'''
\begin{table}[htpb]
\centering
'''
    header += '\\caption{{{}: scores for the \textit{{Default}} and \textit{{Oracle}} experiments on each metric.}}\n'.format(dataset)
    header += '\\label{{tab:scores_{}}}\n'.format(dataset.lower())
    header += r'''
\begin{tabular}{lrrcrr}
    \toprule
    & \multicolumn{2}{c}{Default} & & \multicolumn{2}{c}{Oracle} \\
    \cmidrule{2-3}\cmidrule{5-6}
    Method & Cover & F1 & & Cover & F1 \\
    \midrule

'''
    footer = r'''
    \bottomrule
\end{tabular}
\end{table}
'''

    # Get the max for each metric and experiment
    default_scores_max_cover = default_scores['cover'].max()
    default_scores_max_f1 = default_scores['f1'].max()
    best_scores_max_cover = best_scores['cover'].max()
    best_scores_max_f1 = best_scores['f1'].max()

    # Replace MONGO with MongoDB in method_name
    df['method_name'] = df['method_name'].apply(lambda x: 'MongoDB' if x == 'MONGO' else x)


    # Write the table
    values = ""
    for method_name in default_scores.index:
        row = r'{} & {} & {} & & {} & {} \\'.format(
            method_name.upper(),
            highlight_max(default_scores_max_cover, default_scores.loc[method_name]['cover']),
            highlight_max(default_scores_max_f1, default_scores.loc[method_name]['f1']),
            highlight_max(best_scores_max_cover, best_scores.loc[method_name]['cover']),
            highlight_max(best_scores_max_f1, best_scores.loc[method_name]['f1'])
        )
        values += row + '\n'

    return header + values + footer

# Highlight the max in the latex table
def highlight_max(max_value, value):
    max_value = '{:.2f}'.format(max_value)
    value = '{:.2f}'.format(value)
    if max_value == value:
        return r'\textbf{{{}}}'.format(value)
    else:
        return '{}'.format(value)

def latex_wide_table(df):
    # Get the max for each column
    max_values = df.max()

    # Write row by row (only latex rows, not the header)
    values = ""
    for method_name in df.index:
        values += method_name.upper() + '\n'
        row = r'    '
        for col in df.columns:
            row += '& ' + highlight_max(max_values[col], df.loc[method_name][col]) + ' '
            # add a newline after 4 columns
            cols = len(row.split('&')) - 1
            if cols % 6 == 0:
                if cols == 6:
                    row += '% Overall'
                elif cols == 12:
                    row += '% GraalVM'
                elif cols == 18:
                    row += '% MongoDB'
                elif cols == 24:
                    row += '% SAP HANA'
                row += '\n    '
        values += row + r'\\' + '\n\n'

    return values

def default_and_best_table(dataset_name, df):
    def prepend_dataset_name(df, dataset_name, label):
        return df.rename(columns={col: '{}_{}_{}'.format(dataset_name, label, col)
                                  for col in df.columns})

    default_scores = compute_default_scores(df)
    default_scores = prepend_dataset_name(default_scores, dataset_name, 'default')

    best_scores = compute_best_scores(df)
    best_scores = prepend_dataset_name(best_scores, dataset_name, 'best')

    tb = pd.concat([default_scores, best_scores], axis=1)
    return tb

def check_args():
    if len(sys.argv) != 2:
        print('Usage: python {} summaries.csv'.format(sys.argv[0]))
        sys.exit(1)

if __name__ == "__main__":
    check_args()
    summaries_csv = sys.argv[1]

    df = pd.read_csv(summaries_csv)

    # Exclude datasets that contain '_syn' and '_shuf' in their name
    exclude = ['_syn', '_shuf']
    df = df[~df['dataset'].str.contains('|'.join(exclude))]

    # Extract method name from method column
    df['method_name'] = df['method'].apply(lambda x: x.split('_')[0])

    # Overall scores
    tb = default_and_best_table('Overall', df)

    # Compute the scores for each dataset
    for dataset, name in DATASETS.items():
        _df = df[df['dataset'].str.startswith(name)]
        tb = pd.concat([tb, default_and_best_table(dataset, _df)], axis=1)
#        default_scores = compute_default_scores(_df)
#        best_scores = compute_best_scores(_df)
#        print('------------- Dataset: {}'.format(dataset))
#        print(scores_to_latex(dataset, default_scores, best_scores))

    # Compute the overall scores
#    default_scores = compute_default_scores(df)
#    best_scores = compute_best_scores(df)
#    print('------------- Overall')
#    print(scores_to_latex('Overall', default_scores, best_scores))

#    pd.DataFrame(df['dataset'].unique(), columns=['dataset']).to_csv('datasets.csv', index=False)

    # Save the latex table to a file
    table = latex_wide_table(tb)
    table_filename = 'rq3_cpd_methods_scores.tex'
    with open(table_filename, 'w') as f:
        f.write(table)
    print(f'Latex table saved to {table_filename}')

    # Save the dataframe to a csv file
    csv_filename = 'rq3_cpd_methods_scores.csv'
    tb.to_csv(csv_filename, index=True)
    print(f'Methods scores saved to {csv_filename}')

