"""
    Script responsible for comparing the characteristics of the timeseries from the curated datasets and datasets from other domains.
"""

# %%

import pandas as pd
import glob
import os
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# %%
# Read all csv files
all_files = glob.glob(os.path.join('data/timeseries-stats', "*.csv"))

# %%
list_df = []

for filename in all_files:
    tmp = pd.read_csv(filename, index_col=None, header=0)
    tmp['dataset'] = os.path.basename(filename).split('_')[0]
    list_df.append(tmp)

# %%
df = pd.concat(list_df, ignore_index=True)

# %%
# Deal with heterogenous values in the ADF test 
df['ADF test'] = df['ADF test'].apply(lambda x: 'Stationary' if x == True or x == 'True' else 'Non-stationary')

# %%
# log coeff_var
df['coeff_var_log'] = df['coeff_var'].apply(lambda x: 1 + np.log10(x))


# %%
order = ['SAP', 'Graal', 'MongoDB', 'Finance', 'Human', 'Economics', 'Nature']

# %%
# Setting up the figure
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)
sns.set_context("paper", font_scale=1.7)

# %%
# ASPECT 1: COMPARING WITHIN DOMAINS
systems = ['Graal', 'SAP', 'MongoDB']
performance_df = df[df['dataset'].isin(systems)]

# %%
# LENGTH
g = sns.displot(performance_df, x="size", row="dataset", hue="dataset", kind="kde", fill=True, height=2, aspect=3, facet_kws=dict(sharey=False))

# Removing the y-ticks
g.set(yticks=[])
g.set(xlabel="Time series length")

# Remvoe the dataset = from the title
titles = ['Graal', 'SAP', 'MongoDB']
for ax, title in zip(g.axes.flat, titles):
    ax.set_title(title)

# Drop the legend
g._legend.remove()

plt.savefig('data/timeseries-stats/length_performance.pdf', bbox_inches='tight')



# %%
# --------------------------------------------------
# COEFF VARIANCE
g = sns.displot(performance_df, x="coeff_var_log", row="dataset", hue="dataset", kind="kde", fill=True, height=2, aspect=3, facet_kws=dict(sharey=False))

# Removing the y-ticks
g.set(yticks=[])
g.set(xlabel="Time series length")

# Remvoe the dataset = from the title
titles = ['Graal', 'SAP', 'MongoDB']
for ax, title in zip(g.axes.flat, titles):
    ax.set_title(title)

g.set(xlabel="Coefficient of Variance (log)")
# Limit the x axis to only positive values
g.set(xlim=(0, 4))

# Set the x ticks as 10^0, 10^1, 10^2, 10^3, 10^4
g.set(xticks=[0, 1, 2, 3, 4])
g.set(xticklabels=['$10^0$', '$10^1$', '$10^2$', '$10^3$', '$10^4$'])

# Drop the legend
g._legend.remove()

plt.savefig('data/timeseries-stats/coeffvar_performance.pdf', bbox_inches='tight')



# %%
# SKEWNESS
# Using utility function
# g = plot_distributions_within_performance(performance_df, 'skewness')skewness
g = sns.displot(performance_df, x="skewness", row="dataset", hue="dataset", kind="kde", fill=True, height=2, aspect=3, facet_kws=dict(sharey=False), row_order=systems)

# Removing the y-ticks
g.set(yticks=[])

# Remvoe the dataset = from the title
titles = ['Graal', 'SAP', 'MongoDB']
for ax, title in zip(g.axes.flat, titles):
    ax.set_title(title)

# Limit the x axis to reasonable values
g.set(xlim=(-5, 5))
g.set(xlabel="Skewness")

# Drop the legend
g._legend.remove()

plt.savefig('data/timeseries-stats/skewness_performance.pdf', bbox_inches='tight')


# %%
# KURTOSIS
# Using utility function
# g = plot_distributions_within_performance(performance_df, 'kurtosis')

# There are a handful of time series that are breaking the KDE as they have a kurtosis of 1000+
# As we are truncating the x axis to 100, we can safely remove these outliers
to_plot = performance_df[performance_df['kurtosis'] < 100]

g = sns.displot(to_plot, x="kurtosis", row="dataset", hue="dataset",kind='kde', fill=True, height=2, aspect=3, row_order=systems, facet_kws=dict(sharey=False))

# Removing the y-ticks
g.set(yticks=[])

# Remvoe the dataset = from the title
titles = ['Graal', 'SAP', 'MongoDB']
for ax, title in zip(g.axes.flat, titles):
    ax.set_title(title)


# Drop the legend
g._legend.remove()

# Limit the x axis to reasonable values
g.set(xlim=(-10, 30))
g.set(xlabel="Kurtosis")
plt.savefig('data/timeseries-stats/kurtosis_performance.pdf', bbox_inches='tight')


# %%
# TREND
# g = plot_distributions_within_performance(performance_df, 'spline trend')

g = sns.displot(performance_df, x="spline trend", row="dataset", hue="dataset",kind='kde', fill=True, height=2, aspect=3, row_order=systems, facet_kws=dict(sharey=False))

# Removing the y-ticks
g.set(yticks=[])

# # Remvoe the dataset = from the title
titles = ['Graal', 'SAP', 'MongoDB']
for ax, title in zip(g.axes.flat, titles):
    ax.set_title(title)

# Removing the y-ticks
g.set(yticks=[])

# Limit the x axis to reasonable values
g.set(xlim=(-0.02, 0.02))
g.set(xlabel="Average Slope")
plt.savefig('data/timeseries-stats/trend_performance.pdf', bbox_inches='tight')



# %%
# STATIONARITY

# Plot a bar chart with the count of ADF test in each dataset as a percentage to the dataset size
to_plot = performance_df.groupby(['dataset', 'ADF test']).size().reset_index(name='count')

# Computing the percentages within dataset
to_plot['perc'] = to_plot.groupby('dataset').apply(lambda x: x['count'] / x['count'].sum() * 100).reset_index(drop=True)

# %%
# Plotting a stack bar chart with stationary and non-stationary percentages in each dataset
g = sns.catplot(data=to_plot, x="dataset", y="perc", hue="ADF test", kind='bar', aspect=1.3, palette='Blues', order=systems, edgecolor="0.5")

# Set the y axis as percentage
g.set(ylabel="% of performance timeseries ")

# Set the x axis as "Dataset"
g.set(xlabel="Dataset")

# Annotate the top bar of the plot with the percentages
for p in g.ax.patches:
    # skip the first 
    if p.get_height() == 0:
        continue
    width = p.get_width()
    height = p.get_height()
    x, y = p.get_xy() 
    g.ax.annotate(f'{height:.1f}%', (x + width/2, y + height*1.02), ha='center')


# Drop the original legend
g._legend.remove()
# Include a better legend to the top of the plot
g.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)
# drop the legend borders
g.ax.get_legend().get_frame().set_linewidth(0.0)


# Save the plot
plt.savefig('data/timeseries-stats/stationarity_performance.pdf', bbox_inches='tight')


# %%
# AUTOCORRELATION
def get_percentages(df, groupby, lag):
    """
        Utility function to compute the percentages of a column in a dataframe
    """
    to_plot = df.groupby(groupby).size().reset_index(name='count')

    # Computing the percentages within dataset
    to_plot[f'perc_{lag}'] = to_plot.groupby(groupby[0]).apply(lambda x: x['count'] / x['count'].sum() * 100).reset_index(drop=True)

    return to_plot


lag_1 = get_percentages(performance_df, ['dataset', 'autocorr lag_1'], 1)

lag_5 = get_percentages(performance_df, ['dataset', 'autocorr lag_5'], 5)

lag_10 = get_percentages(performance_df, ['dataset', 'autocorr lag_10'], 10)

to_plot = pd.concat([lag_1, lag_5, lag_10], axis=1)
to_plot['auto_corr'] = to_plot['autocorr lag_1']

# drop duplicated columns
to_plot = to_plot.loc[:,~to_plot.columns.duplicated()]

to_plot = to_plot[['dataset', 'perc_1', 'perc_5', 'perc_10', 'auto_corr']]

# TRanspose the dataframe to plot the percentages as a bar chart
to_plot = to_plot.melt(id_vars=['dataset', 'auto_corr'], var_name='lag', value_name='perc')

# Focus only on the autocorrelated time series
to_plot = to_plot[to_plot['auto_corr'] == True]

# %%
g = sns.catplot(data=to_plot, x="dataset", hue="lag", y='perc', kind='bar', aspect=2.2, palette='Blues', order=systems, edgecolor="0.5")

# annotate bar values
for p in g.ax.patches:

    # skip the first 
    if p.get_height() == 0:
        continue
    width = p.get_width()
    height = p.get_height()
    x, y = p.get_xy() 
    g.ax.annotate(f'{height:.1f}%', (x + width/2, y + height*1.02), ha='center')

# Set the y axis as percentage
g.set(ylabel="% of autocorrelated time series")

# Set the x axis as "Dataset"
g.set(xlabel="Dataset")

# Drop the original legend
g._legend.remove()

# Include a new legend to the top of the plot
g.ax.legend(title = 'Autocorrelation Lag', loc='upper center', bbox_to_anchor=(0.5, 1.22), ncol=3)

# g._legend.set_title('Autocorrelation Lag')

# replace perc_1, perc_5, perc_10 with lag 1, lag 5, lag 10
new_labels = ['1 data-point', '5 data-points', '10 data-points']
for t, l in zip(g.ax.get_legend().texts, new_labels): t.set_text(l)

# remove the lines from the legend
g.ax.get_legend().get_frame().set_linewidth(0.0)

# Save the plot
plt.savefig('data/timeseries-stats/autocorr_performance.pdf', bbox_inches='tight')


# --------------------------------------------------
# ASPECT 2: COMPARING ACROSS DOMAINS
# --------------------------------------------------
 #%%
df['size_log'] = df['size'].apply(lambda x: np.log10(x))

other_domains = ['Finance', 'Human', 'Economics', 'Nature']
other_domains_df = df[df['dataset'].isin(other_domains)]

# get pastel palette without the first three colors 
palette = sns.color_palette('pastel')
palette = palette[3:]

# %%
# LENGTH
g = sns.displot(x="size_log", hue='dataset', data=other_domains_df, kind='kde', fill=True, aspect=1.6, palette=palette, legend=True)

# Set the y axis as "Time series length"
g.set(xlabel="Time series length")

g._legend.set_title('Dataset')
g._legend.set_bbox_to_anchor([0.5, 1.02])  # Adjust anchor position for better visualization
g._legend.set_ncols(len(g._legend.get_lines()))  # Set ncols to the number of legend items
g._legend._loc = 9 


# Set x axis ticks as 10^0, 10^1, 10^2, 10^3, 10^4, 10^5, 10^6
g.set(xticks=[0, 1, 2, 3, 4, 5, 6])
g.set(xticklabels=['$10^0$', '$10^1$', '$10^2$', '$10^3$', '$10^4$', '$10^5$', '$10^6$'])


# Save the plot
plt.savefig('data/timeseries-stats/length_domains.pdf', bbox_inches='tight')


# %%
# --------------------------------------
# COEFF VARIANCE
# --------------------------------------

to_plot = df[df['coeff_var'] > 0]

g = sns.catplot(x="dataset", y="coeff_var", kind="box", data=to_plot, aspect=1.5, order=order, palette='pastel', legend=False)

# change the y-axis to log scale
g.set(yscale="log")

# Set the y axis as "Coefficient of Variance"
g.set(ylabel="Coefficient of Variance")

# Set the x axis as "Dataset"
g.set(xlabel="Dataset")

# Limit the y-axis
g.set(ylim=(0.01, 1000000))

# save the plot
plt.savefig('data/timeseries-stats/coeffvar_domains.pdf', bbox_inches='tight')


# %%
# --------------------------------------
# SKEWNESS
# --------------------------------------
g = sns.catplot(x="dataset", y="skewness", kind="box", data=to_plot, aspect=1.6, order=order, palette='pastel', legend=False)

# Set the y axis as "Coefficient of Variance"
g.set(ylabel="Skewness")

# Set the x axis as "Dataset"
g.set(xlabel="Dataset")

# Set the y-axis with log2
g.set(yscale="symlog", ylim=(-10, 100))

# save the plot
plt.savefig('data/timeseries-stats/skewness_domains.pdf', bbox_inches='tight')


# %%
# --------------------------------------
# KURTOSIS
# --------------------------------------
g = sns.catplot(x="dataset", y="kurtosis", kind="box", data=to_plot, aspect=1.6, order=order, palette='pastel', legend=False)

# Set the y axis as "Coefficient of Variance"
g.set(ylabel="Kurtosis")

# Set the x axis as "Dataset"
g.set(xlabel="Dataset")

# Set the y limit to 100
g.set(ylim=(-10, 60))

# save the plot
plt.savefig('data/timeseries-stats/kurtosis_domains.pdf', bbox_inches='tight')

# %%
# --------------------------------------
# TREND
# --------------------------------------
g = sns.catplot(x="dataset", y="spline trend", kind="box", data=to_plot, aspect=1.6, order=order, palette='pastel', legend=False)

# Set the y axis as "Coefficient of Variance"
g.set(ylabel="Average Slope")

# Set the x axis as "Dataset"
g.set(xlabel="Dataset")

# Set the y limit to 100
g.set(ylim=(-0.02, 0.02))

# save the plot
plt.savefig('data/timeseries-stats/trend_domains.pdf', bbox_inches='tight')


# %%
# --------------------------------------
# STATIONARITY
# --------------------------------------
to_plot = df.groupby('dataset').apply(lambda x: x['ADF test'].value_counts()['Stationary'] / len(x) * 100).reset_index(name='perc')

# Plot
sns.barplot(data=to_plot, x='dataset', y='perc', order=order, edgecolor="0.5", palette='pastel')

# Increase the figure size 
plt.gcf().set_size_inches(8, 5)

# Set the y axis as percentage
plt.ylabel("% of stationary time series")

# Set the x axis as "Dataset"
plt.xlabel("Dataset")

# Annotate the bar values
for p in plt.gca().patches:
    bbox = p.get_extents()
    width = bbox.width
    height = bbox.height
    x, y = bbox.x0, bbox.y0
    plt.gca().annotate(f'{height:.1f}%', (x + width/2, y + height*1.02), ha='center')

# Save the plot
plt.savefig('data/timeseries-stats/stationarity_domains.pdf', bbox_inches='tight')    



# %%
# --------------------------------------
# AUTOCORRELATION
# --------------------------------------
to_plot = df.groupby('dataset').apply(lambda x: sum(x['autocorr lag_1']) / len(x) * 100).reset_index(name='perc')

# Plot
sns.barplot(data=to_plot, x='dataset', y='perc', order=order, edgecolor="0.5", palette='pastel')

# Increase the figure size 
plt.gcf().set_size_inches(8, 5)

# Set the y axis as percentage
plt.ylabel("% of autocorrelated time series")

# Set the x axis as "Dataset"
plt.xlabel("Dataset")

# Annotate the bar values
for p in plt.gca().patches:
    bbox = p.get_extents()
    width = bbox.width
    height = bbox.height
    x, y = bbox.x0, bbox.y0
    plt.gca().annotate(f'{height:.1f}%', (x + width/2, y + height*1.02), ha='center')

# Save the plot
plt.savefig('data/timeseries-stats/autocorrelation_domains.pdf', bbox_inches='tight')    


# %%
# --------------------------------------
#  STATISTICAL TESTS
# --------------------------------------

# Using Mann-whitney U test to compare the distributions of the performance and non-performance datasets
from scipy.stats import mannwhitneyu
from itertools import combinations


def cliffs_delta(x, y):
    """Compute Cliff's Delta."""
    len_x = len(x)
    len_y = len(y)
    numerator = 0.0
    for a in x:
        for b in y:
            if a > b:
                numerator += 1
            elif a < b:
                numerator -= 1
    return numerator / (len_x * len_y)


def interpret_cliffs_delta(d):
    """Interpret the magnitude of Cliff's Delta."""
    if d <= 0.147:
        return 'negligible'
    elif d <= 0.33:
        return 'small'
    elif d <= 0.474:
        return 'medium'
    else:
        return 'large'


def pairwise_mannwhitney_test(df, group_col, value_col):

    # Getting unique groups
    groups = df[group_col].unique()

    # Pair-wise comparison of groups
    results = []

    for combo in combinations(groups, 2):
        group1 = df[df[group_col] == combo[0]][value_col]
        group2 = df[df[group_col] == combo[1]][value_col]
        
        stat, p = mannwhitneyu(group1, group2)
        delta = cliffs_delta(group1, group2)
        interpretation = interpret_cliffs_delta(abs(delta))
        results.append({
            'Group1': combo[0],
            'Group2': combo[1],
            'Statistic': stat,
            'Significant': p < 0.05,
            'p-value': p,
            'Cliffs Delta': delta,
            'Interpretation': interpretation,
        })

    results_df = pd.DataFrame(results)

    return results_df





# %%
# COEFF VARIANCE
coeff_pairwise = pairwise_mannwhitney_test(df, 'dataset', 'coeff_var')
print(coeff_pairwise)


# %%
# SKEWNESS
skewness_pairwise = pairwise_mannwhitney_test(df, 'dataset', 'skewness')
print(skewness_pairwise)

# %%
# KURTOSIS
kurtosis_pairwise = pairwise_mannwhitney_test(df, 'dataset', 'kurtosis')
print(kurtosis_pairwise)

# %%
# TREND
trend_pairwise = pairwise_mannwhitney_test(df, 'dataset', 'spline trend')
print(trend_pairwise)

# %%
