import pickle as pk
import pandas as pd
import numpy as np
import matplotlib.pyplot as pt
import matplotlib as mp
from read_data import read_data
from ordered_problems import problems
from compress_edits import compress_edits
from sklearn.svm import LinearSVC
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import balanced_accuracy_score

if __name__ == "__main__":

    # load data
    df, _, _ = read_data('data.json')
    # omit practice
    df = df[df['problem'] != 'product']

    grouped = df.groupby(['session', 'problem'])
    best_score = 100 * grouped['passed'].max() / grouped['total'].max()
    success = (best_score == 100).astype(int)

    # cdf = compress_edits(df)
    with open('cdf.pkl', 'rb') as f: cdf = pk.load(f)

    max_steps = int(cdf['step'].max())+1
    grouped = cdf.groupby(['session', 'problem'])

    # build up full data set
    features = np.full((len(grouped), 2*max_steps), np.nan)
    labels = np.full(len(grouped), np.nan)
    lengths = np.full(len(grouped), np.nan)
    for g, ((session, problem), group) in enumerate(grouped):
        if pd.isnull(best_score.loc[(session, problem)]): continue

        labels[g] = success.loc[(session, problem)]
        lengths[g] = len(group)

        feature_vector = (group[['startcur','endcur']].values / group[['partial']].apply(len).values).flat
        features[g, :len(feature_vector)] = feature_vector

    # vary leading feature vector length
    accs = {"train": {}, "test": {}}
    baccs = {"train": {}, "test": {}}
    ns = {"train": [[], []], "test": [[], []]} # [tr/ts][0/1][L]
    n_splits = 3
    n_repeats = 10
    for L in range(1, int(lengths[~np.isnan(lengths)].max())):
        samples = (lengths > L)
        inp, out = features[samples, :2*L], labels[samples]

        # make sure enough labels in each class for cross-validation
        if not (1*n_splits <= out.sum() <= len(out) - 1*n_splits): continue

        accs['train'][L], accs['test'][L] = [], []
        baccs['train'][L], baccs['test'][L] = [], []

        # k-fold validation
        # kf = KFold(n_splits=10, shuffle=True)
        # kf = StratifiedKFold(n_splits=n_splits, shuffle=True)
        kf = RepeatedStratifiedKFold(n_repeats=n_repeats, n_splits=n_splits)
        for k, (train, test) in enumerate(kf.split(inp, out)):
            print(f"L={L}, {int(out[train].sum())}|{len(inp)} train, {int(out[test].sum())}|{len(test)} test, fold {k} of {kf.get_n_splits(inp)}")

        # # LOO validation
        # for k in range(len(inp)):
        #     print(f"L={L}, {len(inp)} samples, fold {k} of {len(inp)}")
        #     train = list(range(k)) + list(range(k+1, len(inp)))
        #     test = [k]

            if k == 0:
                for lab in (0, 1):
                    ns['train'][lab].append((out[train] == lab).sum())
                    ns['test'][lab].append((out[test] == lab).sum())

            svc = LinearSVC(max_iter=20000)
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
    pt.title("Cursor-Based Features")
    # pt.xlabel('# leading edits')
    pt.ylabel('# samples')
    pt.xticks([])
    pt.xlim([0, 17])
    pt.ylim([0, 60])
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
    pt.xticks([])
    pt.xlim([0, 17])
    pt.subplot(3,1,3)
    pt.ylabel('balanced\ntest accuracy')
    pt.xlabel("# leading edits used for input features")
    # pt.ylim([ymin-.1, 1.1])
    pt.xlim([0, 17])
    pt.xticks(range(1,17,3), list(map(str, range(1,17,3))))
    pt.tight_layout()
    pt.savefig('classacc.pdf')
    pt.show()
