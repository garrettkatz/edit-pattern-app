import pickle as pk
import pandas as pd
import numpy as np
import matplotlib.pyplot as pt
import matplotlib as mp
from read_data import read_data
from ordered_problems import problems
from sklearn.svm import LinearSVC
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import balanced_accuracy_score

if __name__ == "__main__":

    # load data
    # df, _, _ = read_data('data.json')
    df, _, _ = read_data('../data/aps-keylogger-default-rtdb-export.2024.02.07.json', bad_sessions=[
        '7RKhKKS5PvStLhW6yiof6QCCcNw2',
        'QcbVjFNMVLXDpHq104m5aCyCxnM2',
        'vf7aIkhcqiM7i5G6DndGd9lNfn03',
    ])

    # omit practice
    df = df[df['problem'] != 'product']
    problems = problems['name'].values
    problems = problems[problems != 'product']

    # list session ids
    sessions = df['session'].unique()
    print(sessions)

    # group by attempt
    grouped = df.groupby(['session', 'problem'])

    # load compressed edits to get num small steps of each one
    with open('cdf.pkl', 'rb') as f: cdf = pk.load(f)

    max_steps = int(cdf['step'].max())+1
    c_grouped = cdf.groupby(['session', 'problem'])

    # build datasets for each leading portion corresponding to compressed edits
    features = {L:[] for L in range(1, max_steps+1)}
    labels = {L:[] for L in range(1, max_steps+1)}
    for subject, session in enumerate(sessions):
        for p, problem in enumerate(problems):

            group = grouped.get_group((session, problem))
            c_group = c_grouped.get_group((session, problem)).set_index('step')

            # omit skipped
            if pd.isnull(group['partial']).any(): continue

            success = (group['passed'] == group['total']).any()

            for L in range(1, max_steps):

                # omit if fewer than L+1 compressed edits
                if len(c_group) <= L: continue

                # discard trailing edits
                smallsteps = c_group.loc[float(L-1), 'smallstep']
                group_L = group[group['step'] <= smallsteps]

                # # omit if only one edit
                # if len(group_L) <= 1: continue

                tms = group_L['time'].values
                lens = group_L['partial'].apply(len).values
                ins = group_L['newcode'].apply(len).values
                dels = group_L['oldcode'].apply(len).values
                idx = group_L['index'].values
                word = group_L['newcode'].str.fullmatch("[a-zA-Z0-9_]+").values
                # group_L['word'] = word
                edge = (idx + ins > lens - 2)
                rev = (dels > 0) | (idx + ins < lens)
                edge[0], rev[0] = False, False # don't count signature
                # group_L['rev'] = rev

                IKI = tms[1:] - tms[:-1]
                inword = word[1:] & word[:-1]

                pause = IKI > (IKI.mean() + 2*IKI.std())
                num_bursts = (pause[1:] & ~pause[:-1]).sum()

                feature_vector = []
                feature_vector.append(IKI[0]) # initial pause time
                feature_vector.append(pause.sum()) # number of pauses
                feature_vector.extend([IKI.mean(), np.median(IKI), IKI.std(), IKI.max()]) # IKI stats
                feature_vector.extend([ # in/between word IKI 
                    IKI[inword].mean() if (inword).sum() > 0 else 0,
                    IKI[inword].std() if (inword).sum() > 0 else 0,
                    IKI[inword].min() if (inword).sum() > 0 else 0,
                    IKI[inword].max() if (inword).sum() > 0 else 0,
                    IKI[~inword].mean() if (~inword).sum() > 0 else 0,
                    IKI[~inword].std() if (~inword).sum() > 0 else 0,
                    IKI[~inword].min() if (~inword).sum() > 0 else 0,
                    IKI[~inword].max() if (~inword).sum() > 0 else 0,
                ])
                feature_vector.extend([rev.sum(), (rev & edge).sum(), (rev & ~edge).sum()]) # revisions (total, leading edge, in text)
                feature_vector.append((dels > 0).sum()) # number of delete/backspace keystrokes
                feature_vector.extend([(lens[-1] - lens[0]) / ins.sum(), (edge & (ins > 0)).sum() / ins.sum()]) # % characters in final text and leading edge
                feature_vector.append(num_bursts)

                # do not include samples with NaNs
                if np.isnan(feature_vector).any():
                    print(group_L)
                    print(feature_vector)
                    input('...')
                    continue

                features[L].append(feature_vector)
                labels[L].append(success)

    # vary num leading edits
    accs = {"train": {}, "test": {}}
    baccs = {"train": {}, "test": {}}
    ns = {"train": [[], []], "test": [[], []]} # [tr/ts][0/1][L]
    min_samps = 5
    n_splits = 3
    n_repeats = 10
    for L in sorted(features.keys()):
        inp, out = np.array(features[L]), np.array(labels[L])

        # make sure enough labels in each class for cross-validation
        if not (min_samps*n_splits <= out.sum() <= len(out) - min_samps*n_splits): continue

        accs['train'][L], accs['test'][L] = [], []
        baccs['train'][L], baccs['test'][L] = [], []

        # k-fold validation
        kf = RepeatedStratifiedKFold(n_repeats=n_repeats, n_splits=n_splits)
        for k, (train, test) in enumerate(kf.split(inp, out)):
            print(f"L={L}, {int(out[train].sum())}|{len(inp)} train, {int(out[test].sum())}|{len(test)} test, fold {k} of {kf.get_n_splits(inp)}")

            if k == 0:
                for lab in (0, 1):
                    ns['train'][lab].append((out[train] == lab).sum())
                    ns['test'][lab].append((out[test] == lab).sum())

            svc = LinearSVC(dual='auto', max_iter=100_000)
            svc.fit(inp[train], out[train])
            accs['train'][L].append(svc.score(inp[train], out[train]))
            accs['test'][L].append(svc.score(inp[test], out[test]))
            baccs['train'][L].append(balanced_accuracy_score(out[train], svc.predict(inp[train])))
            baccs['test'][L].append(balanced_accuracy_score(out[test], svc.predict(inp[test])))

    Ls = np.array(sorted(accs['test'].keys()))

    mp.rcParams['font.family'] = 'serif'
    mp.rcParams['font.size'] = 8
    mp.rcParams['legend.handlelength'] = .75
    mp.rcParams['legend.handleheight'] = .75

    pt.figure(figsize=(3.75, 4.5))

    # example counts
    pt.subplot(3,1,1)
    width = .9
    pt.bar(Ls, ns['train'][0], width, label='Train 0', linestyle=':', ec='k', fc=(.7,)*3)
    pt.bar(Ls, ns['train'][1], width, label='Train 1', linestyle=':', ec='k', fc='w', bottom=ns['train'][0])
    pt.bar(Ls, ns['test'][0], width, label='Test 0', linestyle='-', ec='k', fc=(.7,)*3, bottom=np.array(ns['train'][0])+np.array(ns['train'][1]))
    pt.bar(Ls, ns['test'][1], width, label='Test 1', linestyle='-', ec='k', fc='w', bottom=np.array(ns['train'][0])+np.array(ns['train'][1])+np.array(ns['test'][0]))
    pt.title("Timing-Based Features")
    # pt.xlabel('# leading edits')
    pt.ylabel('# samples')
    pt.xticks([])
    # pt.xlim([0, 17])
    pt.ylim([0, 120])
    pt.legend(ncol=4, fontsize=8, columnspacing=.5, loc='upper center')

    # for L in Ls: print(accs[L])
    ymin = 1
    for label in ('test', 'train'):
        for a,acc in enumerate([accs, baccs]):
            pt.subplot(3,1,a+2)
            avg = np.array([np.mean(acc[label][L]) for L in Ls])
            std = np.array([np.std(acc[label][L]) for L in Ls])
            ls = '-' if label == 'test' else ':'
            if label=='test':
                pt.fill_between(Ls, avg-std, avg+std, color=(.75,)*3)
                for L in Ls:
                    pts = acc[label][L]
                    if len(pts) > 0: ymin = min(ymin, min(pts))
                    # pt.plot(L + np.random.uniform(-.25, .25, len(pts)), pts + np.random.uniform(-.01, .01, len(pts)), '.', color=(.5,)*3)
                    pt.plot([L]*len(pts), pts, '.', color=(.5,)*3)
            pt.plot(Ls, avg, 'k' + ls, label=label)

    pt.subplot(3,1,2)
    pt.ylabel('unbalanced\ntest accuracy')
    # pt.ylim([ymin-.1, 1.1])
    pt.ylim([.4, 1])
    pt.xticks([])
    # pt.xlim([0, 17])
    pt.subplot(3,1,3)
    pt.ylabel('balanced\ntest accuracy')
    pt.xlabel("# leading edits used for input features")
    pt.ylim([.3, 1.])
    # pt.ylim([ymin-.1, 1.1])
    # pt.xlim([0, 17])
    # pt.xticks(range(1,17,3), list(map(str, range(1,17,3))))
    pt.tight_layout()
    pt.savefig('classacc_timing.pdf')
    pt.show()
