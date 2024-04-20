import pickle as pk
import pandas as pd
import numpy as np
import matplotlib.pyplot as pt
import matplotlib as mp
from read_data import read_data
from ordered_problems import problems

def compress_edits(df):
    # merge consecutive insertions and deletions
    # df.columns = ['session', 'problem', 'total', 'step', 'time', 'newcode', 'oldcode', 'index', 'passed', 'partial'])

    print('*' * 80)

    cdf_cols = ['session', 'problem', 'step', 'time', 'newcode', 'oldcode', 'startcur', 'endcur', 'partial', 'smallstep']
    cdf_data = []
    for (session, problem), group in df.groupby(['session', 'problem']):

        # handle skipped/omitted attempts
        if pd.isnull(group['time']).any():
            cdf_data.append([session, problem] + [np.nan]*(len(cdf_cols)-2))
            continue

        group = group.set_index('step')
        cidx, pidx = group.index[1:], group.index[:-1] # current, prev index

        group['oldlen'] = group['oldcode'].apply(len)
        group['newlen'] = group['newcode'].apply(len)

        group['insert'] = (group['oldlen'] == 0)
        group['delete'] = (group['newlen'] == 0)
        group['replace'] = ~(group['insert'] | group['delete'])

        group['oldcur'] = group['index'] + group['oldlen'].where(group['delete'], 0)
        group['newcur'] = group['index'] + group['newlen'].where(~group['delete'], 0)
        group['motion'] = 0
        group.loc[group['oldcur'] - group['newcur'] > 0, 'motion'] = +1
        group.loc[group['oldcur'] - group['newcur'] < 0, 'motion'] = -1

        group['contig'] = False # if current edit cursor movement is contiguous with prev
        group.loc[cidx, 'contig'] = (group.loc[pidx, 'newcur'].values == group.loc[cidx, 'oldcur'].values)
        group['moment'] = False # if current edit cursor movement is same motion as prev
        group.loc[cidx, 'moment'] = (group.loc[pidx, 'motion'].values == group.loc[cidx, 'motion'].values)

        # print(group)
        startcur = group.loc[0, 'newcur']
        endtime = group.loc[0, 'time']
        newcode = oldcode = ''
        bigstep = 0
        for step, row in group.iterrows():
            if step == 0: continue

            # edit pattern change from previous to current row
            state_change = not (row['contig'] and row['moment'])

            if state_change:

                # print(f"state change: {row['oldcur']}->{row['newcur']} | {repr(row['oldcode'])} -> {repr(row['newcode'])}")
                cdf_data.append([session, problem, bigstep, endtime, newcode, oldcode, startcur, row['oldcur'], partial, step])
                newcode, oldcode, startcur = row[['newcode', 'oldcode', 'oldcur']]
                bigstep += 1

            else:

                newcode = newcode + row['newcode']
                oldcode = row['oldcode'] + oldcode

            endtime, partial = row[['time', 'partial']]
            # print(repr(partial))

        cdf_data.append([session, problem, bigstep, endtime, newcode, oldcode, startcur, row['newcur'], partial, step])

        # break
        # print(pd.DataFrame(columns = cdf_cols, data = cdf_data))
        # input('...')

    return pd.DataFrame(columns = cdf_cols, data = cdf_data)

if __name__ == "__main__":

    # df, _, _ = read_data('data.json')
    df, _, _ = read_data('../data/aps-keylogger-default-rtdb-export.2024.02.07.json', bad_sessions=[
        '7RKhKKS5PvStLhW6yiof6QCCcNw2',
        'QcbVjFNMVLXDpHq104m5aCyCxnM2',
        'vf7aIkhcqiM7i5G6DndGd9lNfn03',
    ])

    # omit practice
    df = df[df['problem'] != 'product']

    cdf = compress_edits(df)
    with open('cdf.pkl', 'wb') as f: pk.dump(cdf, f)

    with open('cdf.pkl', 'rb') as f: cdf = pk.load(f)
    print(cdf)

    grouped = cdf.groupby(['session', 'problem'])
    num_steps = grouped['step'].max()+1
    print(num_steps)

    half_features = 3
    print((num_steps >= half_features))
    print((num_steps >= half_features).sum())
    print((num_steps >= half_features).sum() / len(grouped))

    mp.rcParams['font.family'] = 'serif'

    pt.figure(figsize=(4,3))
    pt.hist(num_steps, bins=20, edgecolor='k', facecolor='w')
    pt.xlabel('Big steps')
    pt.ylabel('Frequency')
    pt.tight_layout()
    pt.show()

    # print(num_steps.min(), num_steps.max())


