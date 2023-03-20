import pandas as pd
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as pt
from read_data import read_data
from ordered_problems import problems

if __name__ == "__main__":    

    pd.set_option('display.max_colwidth', None)

    df, responses, bad_sessions = read_data('data.json')
    sessions = df['session'].unique()

    grouped = df.groupby(['session', 'problem'])
    best_score = 100 * grouped['passed'].max() / grouped['total'].max()

    plot_data = responses.set_index(['session', 'problem'])
    plot_data['score'] = best_score
    plot_data['time'] = grouped['time'].max()

    # drop skipped attempts and practice
    plot_data = plot_data[~pd.isnull(plot_data['score'])]
    plot_data = plot_data.drop(index='product', level=1)

    print(plot_data)

    print(plot_data.dtypes)
    print(plot_data['concept'])

    # questions = ["familiar", "advanced", "challenge"]
    questions = ["familiar", "advanced"]
    labels = ["Familiarity", "Difficulty"]

    # omit missing data rows
    plot_data = plot_data[(plot_data[questions] != '').all(axis=1)]

    # pt.figure(figsize=(4,3))
    # for c,(col, label) in enumerate(zip(questions, labels)):
    #     pt.subplot(len(questions),1,c+1)
    #     for s, (marker, session) in enumerate(zip("+x.", sessions)):
    #         dat = plot_data.xs(session, level='session')        
    #         # pt.scatter(plot_data[col].astype(int), plot_data['score'] + 0.01*np.random.rand(plot_data.shape[0]))
    #         pt.plot(dat['score'], dat[col].astype(int), linestyle='none', color='k', marker=marker)

    #     # https://stackoverflow.com/questions/26447191/how-to-add-trendline-in-python-matplotlib-dot-scatter-graphs
    #     sc, srv = plot_data['score'], plot_data[col].astype(int)
    #     sc, srv = sc[~pd.isnull(sc)], srv[~pd.isnull(sc)]
    #     z = np.polyfit(sc, srv, 1)
    #     p = np.poly1d(z)
    #     pt.plot([sc.min(), sc.max()], [p(sc.min()), p(sc.max())], "k:")

    #     pt.ylabel(label)
    # pt.xlabel('% tests passed')
    # pt.tight_layout()
    # pt.savefig("perception.pdf")
    # pt.show()

    mp.rcParams['font.size'] = 8
    mp.rcParams['font.family'] = 'serif'
    pt.figure(figsize=(4,2))
    for c,(col, label) in enumerate(zip(questions, labels)):
        pt.subplot(1, len(questions), c+1)
        for s, (marker, session) in enumerate(zip("+x.", sessions)):
            dat = plot_data.xs(session, level='session')        
            # pt.scatter(plot_data[col].astype(int), plot_data['score'] + 0.01*np.random.rand(plot_data.shape[0]))
            pt.plot(dat['score'], dat[col].astype(int), linestyle='none', color='k', marker=marker)

        # https://stackoverflow.com/questions/26447191/how-to-add-trendline-in-python-matplotlib-dot-scatter-graphs
        sc, srv = plot_data['score'], plot_data[col].astype(int)
        sc, srv = sc[~pd.isnull(sc)], srv[~pd.isnull(sc)]
        z = np.polyfit(sc, srv, 1)
        p = np.poly1d(z)
        pt.plot([sc.min(), sc.max()], [p(sc.min()), p(sc.max())], "k:")

        # pt.ylabel(label)
        pt.title(label)
        if c == 0: pt.ylabel("Rating")
        if c == 1: pt.yticks([])
        pt.ylim([-.1, 10.1])
    pt.gcf().supxlabel('% tests passed')
    pt.tight_layout()
    pt.savefig("perception.pdf")
    pt.show()

    # time limits and surveys
    problems = problems.set_index('name')
    pt.figure(figsize=(4,3))
    for s, (marker, session) in enumerate(zip("+x.", sessions)):
        dat = plot_data.xs(session, level='session')
        print(dat)
        dat.loc[:, 'time'] = dat['time'] / problems.loc[dat.index, 'seconds']

        # pt.scatter(plot_data[col].astype(int), plot_data['score'] + 0.01*np.random.rand(plot_data.shape[0]))
        pt.plot(dat['time'], dat['challenge'].astype(int), linestyle='none', color='k', marker=marker)

        # # https://stackoverflow.com/questions/26447191/how-to-add-trendline-in-python-matplotlib-dot-scatter-graphs
        # sc, srv = plot_data['score'], plot_data[col].astype(int)
        # sc, srv = sc[~pd.isnull(sc)], srv[~pd.isnull(sc)]
        # z = np.polyfit(sc, srv, 1)
        # p = np.poly1d(z)
        # pt.plot([sc.min(), sc.max()], [p(sc.min()), p(sc.max())], "k:")

    pt.ylabel('Time wanted')
    pt.xlabel('% time taken')
    pt.tight_layout()
    pt.savefig("timing.pdf")
    pt.show()
    

