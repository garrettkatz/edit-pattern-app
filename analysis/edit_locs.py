import pandas as pd
import numpy as np
import matplotlib.pyplot as pt
from read_data import read_data
from ordered_problems import problems

if __name__ == "__main__":    

    problems = problems['name'].values

    df, _, _ = read_data('data.json')
    sessions = df['session'].unique()

    # omit practice
    df = df[df['problem'] != 'product']
    # df = df[df['step'] > 0] # don't count original function signature

    grouped = df.groupby(['session', 'problem'])

    # # all

    # fig = pt.figure(figsize=(16,12))

    # for sp, ((session, problem), group) in enumerate(grouped):

    #     # omit skipped
    #     if pd.isnull(group['partial']).any(): continue

    #     subject = (sessions == session).argmax()
    #     success = (group['passed'] == group['total']).any()

    #     tms = group['time'].values
    #     lens = group['partial'].apply(len).values
    #     ins = group['newcode'].apply(len).values
    #     dels = group['oldcode'].apply(len).values
    #     idx = group['index'].values

    #     x = tms
    #     # x = np.arange(len(group))

    #     pt.subplot(6, 8, sp+1)

    #     # pt.plot(x, lens, ':', color=(.5,)*3)
    #     # pt.plot(x[1:], idx[1:], '-', color='k') # omit signature "edit"
    #     pt.step(x, lens, ':', color=(.5,)*3)
    #     pt.step(x[1:], idx[1:], '-', color='k') # omit signature "edit"

    #     # pt.plot(x, idx + ins, '-', color='b')
    #     # pt.plot(x, idx + dels, '-', color='r')
    #     # pt.bar(x, ins, 1, idx, color='b')
    #     # pt.bar(x, -dels, 1, idx, color='r')

    #     pt.title(f"{problem}: {subject} {'PASS' if success else 'FAIL'}")

    # fig.supxlabel('Edit')
    # fig.supylabel('Location')
    # pt.tight_layout()
    # pt.savefig('edit_locs.pdf')
    # pt.show()

    # # vertical
    # pidxs = list(range(len(problems)))
    # pidxs = [0,1,2,4,7,8,9,11,12,13,15]

    # max_y = {} # max loc by problem
    # max_x = {} # max edit by participant

    # fig, axs = pt.subplots(len(pidxs), 3, constrained_layout=True, figsize=(4,12))
    # for p, pidx in enumerate(pidxs):
    #     for subject, session in enumerate(sessions):

    #         ax = axs[p][subject]
    #         pt.sca(ax)
    #         problem = problems[pidx]

    #         group = grouped.get_group((session, problem))

    #         if subject == 0: pt.ylabel(f"{pidx}: {problem}")
    #         # if subject == 0: pt.ylabel(f"{problem}")

    #         # omit skipped
    #         if pd.isnull(group['partial']).any(): continue
    
    #         success = (group['passed'] == group['total']).any()
    
    #         tms = group['time'].values
    #         lens = group['partial'].apply(len).values
    #         ins = group['newcode'].apply(len).values
    #         dels = group['oldcode'].apply(len).values
    #         idx = group['index'].values
    
    #         x = tms
    #         # x = np.arange(len(group))

    #         pt.step(x, lens, ':', color=(.5,)*3)
    #         pt.step(x[1:], idx[1:], '-', color='k') # omit signature "edit"

    #         max_x[subject] = max(x.max(), max_x.get(subject, 0))
    #         max_y[p] = max(lens.max(), idx[1:].max(), max_y.get(p, 0))
    
    #         # pt.title(f"{'+x.'[subject]} [{'PASS' if success else 'FAIL'}]")
    #         if p == 0: pt.title(f"{'+x.'[subject]}")

    #         if not success:
    #             for spine in ax.spines.values(): spine.set_linestyle((0,(8,5)))

    # for p, pidx in enumerate(pidxs):
    #     for subject, session in enumerate(sessions):
    #         pt.sca(axs[p][subject])
    #         pt.xlim([0, max_x[subject]])
    #         pt.ylim([0, max_y[p]])
    #         if subject > 0: pt.yticks([])
    #         if p < len(pidxs)-1: pt.xticks([])

    # fig.supxlabel('Time (s)')
    # fig.supylabel('Position')
    # pt.savefig('cursors.pdf')
    # pt.show()

    # horizontal
    pidxs = list(range(len(problems)))
    pidxs = [0,1,2,4,5,6,7,8,9,11,12,13,15]

    max_y = {}
    max_x = {}

    fig, axs = pt.subplots(3, len(pidxs), constrained_layout=True, figsize=(9.5,2.75))
    for subject, session in enumerate(sessions):
        for p, pidx in enumerate(pidxs):

            ax = axs[subject][p]
            pt.sca(ax)
            problem = problems[pidx]

            group = grouped.get_group((session, problem))

            # if subject == 0: pt.title(f"{pidx}: {problem}", fontsize=8)
            if subject == 0: pt.title(f"{problem}", fontsize=8)

            # omit skipped
            if pd.isnull(group['partial']).any(): continue
    
            success = (group['passed'] == group['total']).any()
    
            tms = group['time'].values
            lens = group['partial'].apply(len).values
            ins = group['newcode'].apply(len).values
            dels = group['oldcode'].apply(len).values
            idx = group['index'].values
    
            x = tms
            # x = np.arange(len(group))

            # pt.step(x, lens, ':', color=(.5,)*3)
            pt.step(x, lens, '-', color=(.5,)*3)
            pt.step(x[1:], idx[1:], '-', color='k') # omit signature "edit"

            max_x[p] = max(x.max(), max_x.get(p, 0))
            if len(x) > 1:
                max_y[subject] = max(lens.max(), idx[1:].max(), max_y.get(subject, 0))
    
            # pt.ylabel(f"{'+x.'[subject]} [{'PASS' if success else 'FAIL'}]")
            if p == len(pidxs)-1:
                ax.yaxis.set_label_position("right")
                pt.ylabel(f" {'+x.'[subject]}", rotation=0)

            if not success:
                for spine in ax.spines.values(): spine.set_linestyle((0,(8,5)))

    for subject, session in enumerate(sessions):
        for p, pidx in enumerate(pidxs):
            pt.sca(axs[subject][p])
            pt.xlim([0, max_x[p]])
            pt.ylim([0, max_y[subject]])
            if subject < len(sessions)-1: pt.xticks([])
            if p > 0: pt.yticks([])

    fig.supxlabel('Time (s)', fontsize=10)
    fig.supylabel('Characters', fontsize=10)
    pt.savefig('cursors.pdf')
    pt.show()



