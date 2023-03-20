import pandas as pd
import numpy as np
import matplotlib.pyplot as pt
import matplotlib as mp
from read_data import read_data
from ordered_problems import problems
from drop import drop

time_limits = problems['seconds'].values
problems = problems['name'].values

df, _, _ = read_data('data.json')
sessions = df['session'].unique()
print(sessions)

grouped = df.groupby(['session', 'problem'])
best_score = 100 * grouped['passed'].max() / grouped['total'].max()
code_time = grouped['time'].max()

print(best_score)
print(code_time)

mp.rcParams['font.family'] = 'serif'

# scatterplots
# pt.figure(figsize=(4,6))

# # coding time vs test scores
# pt.subplot(2,1,1)
# for s, (marker, session) in enumerate(zip("+x.", sessions)):
#     bs = best_score.xs(session, level='session')
#     ct = code_time.xs(session, level='session')
#     pt.plot(ct.values, bs.values, linestyle='none', color='k', marker=marker)

# pt.xlabel("Coding time (s)")
# pt.ylabel("Tests passed percentage")
# # pt.xscale('log')

# actual and max coding time
# pt.subplot(2,1,1)
# for s, (marker, session) in enumerate(zip("+x.", sessions)):
#     ct = code_time.xs(session, level='session')
#     ct = ct[problems]
#     pt.plot(range(len(problems)), ct.values, linestyle='none', color='k', marker=marker)
# pt.plot(range(len(problems)), time_limits, 'k:')
# pt.ylabel("Coding time (s)")
# pt.xticks([])

# pt.subplot(2,1,2)
mp.rcParams['font.size'] = 8
pt.figure(figsize=(3.5, 2))
x, y = [], []
for s, (marker, session) in enumerate(zip("+x.", sessions)):
    bs = best_score.xs(session, level='session')
    bs = bs[problems]
    pt.plot(range(len(problems)), bs.values, linestyle='none', color='k', marker=marker)
    x.extend(range(len(problems)))
    y.extend(bs[problems].values)

# https://stackoverflow.com/questions/26447191/how-to-add-trendline-in-python-matplotlib-dot-scatter-graphs
x, y = np.array(x), np.array(y)
z = np.polyfit(x[~np.isnan(y)], y[~np.isnan(y)], 1)
p = np.poly1d(z)
pt.plot(np.arange(len(problems)), p(np.arange(len(problems))), "k:")
print(p(np.arange(len(problems))))

pt.xticks(range(len(problems)), problems, rotation=90)
pt.ylabel("% tests passed")

# pt.legend()
pt.tight_layout()
pt.savefig('problem_difficulty.pdf')
pt.show()

# histogram
mp.rcParams['font.size'] = 8
pt.figure(figsize=(3.5, 1.75))
pt.subplot(1,2,1)
bins = np.unique(best_score.values)
bins = bins[~np.isnan(bins)]
bins = (bins[1:] + bins[:-1]) / 2
bins = np.insert(bins, 0, -bins[0])
bins = np.append(bins, [100 + (100 - bins[-1])])
print(bins)
pt.hist(best_score.values, facecolor='w', edgecolor='k', bins=bins)
pt.xlabel("% tests passed")
pt.ylabel("Frequency")

# boxplot
pt.subplot(1,2,2)
x = []
for session in sessions:
    bs = best_score.xs(session, level='session')
    bs = bs[pd.notnull(bs)]
    x.append(bs)

# pt.boxplot(x, medianprops = {'color':'k', 'linestyle':':', 'linewidth':1}, widths=.8)
parts = pt.violinplot(x, widths=.8)
for pc in parts['bodies']:
    pc.set_edgecolor('black')
    pc.set_facecolor((.8,.8,.8))
for key in ['cmins', 'cmaxes', 'cbars']:
    parts[key].set_edgecolor((.8,.8,.8))
for k,bs in enumerate(x):
    pt.plot(np.random.uniform(-.1, +.1, len(bs)) + (k+1), np.random.uniform(-3, 3, len(bs)) + bs, '.', color=(.25,)*3)
pt.xticks(range(1,4), list("+x."))
pt.xlabel("Participant")
pt.ylabel("% tests passed")
pt.tight_layout()
pt.savefig('bimodal_performance.pdf')
pt.show()



