import numpy as np
import json
import pandas as pd
from drop import drop

def read_data(fname):
    
    # read and parse the json data
    with open(fname,'r') as f: data = json.load(f)
    
    # Iterate over sessions, skip ones with errors
    session_ids = list(data.keys())
    bad_sessions = []
    df_data = []
    survey_data = []
    for sid, session_id in enumerate(session_ids):
        print(f"session id {session_id}")
    
        # try:
        if True:
    
            # keystroke data: list of problems, each a dictionary mapping timesteps to edit data
            keystrokes = data[session_id]['keystrokes']
            surveys = data[session_id]['surveys']
        
            for p,problem in enumerate(keystrokes):
        
                # timestamps of edits
                timestamps = np.array(sorted(problem.keys()))

                # convert timestamps to seconds elapsed
                timepoints = timestamps.astype(int)
                timepoints = (timepoints - timepoints[0]) / 1000

                # total number of test cases
                total_tests = problem[timestamps[0]]['total_testcases']

                # use function name as problem identifier
                prob_name = problem[timestamps[0]]['newcode'].strip()
                prob_name = prob_name[4:prob_name.find("(")]

                # patch for mismatched signatures/problem names
                if prob_name == "divisor_list":
                    if p == 5: prob_name = "divisors"
                    if p == 12: prob_name = "divisors2"
                if prob_name == "n_choose_k":
                    prob_name = "binomial"

                # save survey data
                survey_data.append([session_id, prob_name] + surveys[prob_name])

                # reconstruct partial codes
                code = ""

                # extract records for each timestamp
                for t,timestamp in enumerate(timestamps):
        
                    # record for current edit
                    record = problem[timestamp]
                    nc, oc, idx, tst = tuple(record.get(k, None) for k in ('newcode', 'oldcode', 'index', 'correct_testcases'))

                    # apply edit to code
                    code = code[:idx] + nc + code[idx+len(oc):]

                    # add record to df data
                    df_data.append([session_id, prob_name, total_tests, t, timepoints[t], nc, oc, idx, tst, code])

        # except:
        else:
    
            bad_sessions.append(session_id)

    # wrap dataframes
    df = pd.DataFrame(data=df_data, columns = ['session', 'problem', 'total', 'step', 'time', 'newcode', 'oldcode', 'index', 'passed', 'partial'])
    responses = pd.DataFrame(data=survey_data, columns = ['session', 'problem', 'familiar', 'advanced', 'challenge', 'concept'])

    # omit data where participant logged out and exceeded time limit
    df = df[df['time'] < 1000]

    # mark dropped problems as missing data with NaNs
    nan_cols = df.columns[2:]
    for session, problem in drop:
        df.loc[(df['session'] == session) & (df['problem'] ==  problem), nan_cols] = np.nan

    return df, responses, bad_sessions

if __name__ == "__main__":    

    df, responses, bad_sessions = read_data('data.json')
    print(df)
    print(responses)
    print(bad_sessions)

    # # print long-format responses
    # responses = responses.set_index(['session', 'problem'])
    # for (session, problem) in responses.index:
    #     print(session, problem)
    #     print(responses.loc[(session, problem), 'concept'])

