import numpy as np
import pandas as pd

def crop_time(df):
    df_size = len(df)
    cropped_df = df[0:int(df_size)]
    return cropped_df

def calc_dwell_time_travis(df):
    # Find index of each no-reward tone
    codes = [17,29,41,53] # no-reward tone codes (0% offer tone)
    time_stamps_tone = df.time[df.b_code.isin(codes)]
    codes = [63,66,69,72] # Exit codes & Entry codes -> in case exits wrong way
    time_stamps_exit = df.time[df.b_code.isin(codes)]
    # Calculate time to next exit
    intervals = np.zeros_like(time_stamps_tone.values)
    i=0
    for event in time_stamps_tone.values:
        diffs = time_stamps_exit-event
        interval = np.min(diffs[diffs>0])
        intervals[i] = interval/1000
        i=i+1
    no_r_dwell = np.NaN
    if ~(np.sum(intervals)==0):
        no_r_dwell = np.nanmedian(intervals)

    # Find index of each reward tone
    codes = [20,32,44,56] # reward tone codes
    time_stamps_tone = df.time[df.b_code.isin(codes)]
    # codes = [63,66,69,72] # Exit codes
    codes = [16,28,40,52,63,66,69,72] # Calculate time from entry to exit, back exit, or to pellet dispersal
    time_stamps_exit = df.time[df.b_code.isin(codes)]
    # Calculate time to next pellet eaten or exit
    intervals = np.zeros_like(time_stamps_tone.values)
    i=0
    for event in time_stamps_tone.values:
        diffs = time_stamps_exit-event
        interval = np.min(diffs[diffs>0])
        intervals[i] = interval/1000
        i=i+1
    r_dwell = np.NaN
    if ~(np.sum(intervals)==0):
        r_dwell = np.nanmedian(intervals)
    return [r_dwell, no_r_dwell]

def calc_dwell_time_dist(df):
    """
    New function to calculate dwell time for 0% and 100% prob tone using sharp entry - sharp exit after tone
    """
    ##################### NO REWARD DWELL TIME #################################

    zero_offer_tone = [17,29,41,53] #0% offer tone
    sharp_exit = [63,66,69,72] # Exit codes & Entry codes -> in case exits wrong way
    sharp_entry = [61, 64, 67, 70] #& Entry codes -> in case exits wrong way

    #find sharp entries associated with 0% offer tone
    no_rtone_idx = np.where(df.b_code.isin(zero_offer_tone))[0]
    no_r_entry_idxs = []
    for no_rtone in no_rtone_idx:
        r_num = zero_offer_tone.index(df.b_code[no_rtone]) # get which restaurant the 0% offer came from
        next_events = df.b_code[no_rtone:no_rtone+10].isin([sharp_entry[r_num]]) # find next "sharp entry" for that rstrnt
        delta_idx_entry = next((i for i, j in enumerate(next_events) if j), np.nan)
        next_entry = no_rtone + delta_idx_entry
        if ~np.isnan(next_entry):
            no_r_entry_idxs.append(next_entry)

    time_stamps_enter = df.time[no_r_entry_idxs]
    time_stamps_exit = df.time[df.b_code.isin(sharp_exit)]

    # Calculate time to next exit
    intervals = np.zeros_like(time_stamps_enter.values)
    i=0
    for event in time_stamps_enter.values:
        diffs = time_stamps_exit-event # calculate time difference between one event and others
        interval = np.min(diffs[diffs>0])# take the min of only the positive diffs
        intervals[i] = interval/1000 # get proper units
        i=i+1
    no_r_dwellt_dist = intervals
    no_r_dwellt_median = np.NaN
    if ~(np.sum(intervals)==0):
        no_r_dwellt_median = np.nanmedian(intervals)

    ##################### REWARD DWELL TIME #################################

    hundy_offer_tone = [20,32,44,56] # 100% reward tone codes
    rwd_taken = [16,28,40,52]

    # Calculate time from entry to exit, back exit, or to pellet dispersal
    rtone_idx = np.where(df.b_code.isin(hundy_offer_tone))[0]
    r_entry_idxs = []
    for rtone in rtone_idx:
        r_num = hundy_offer_tone.index(df.b_code[rtone]) # get which restaurant the 100% offer came from
        next_events = df.b_code[rtone:rtone+10].isin([sharp_entry[r_num]]) # find next "sharp entry" for that rstrnt
        delta_idx_entry = next((i for i, j in enumerate(next_events) if j), np.nan)
        next_entry = rtone + delta_idx_entry
        if ~np.isnan(next_entry):
            r_entry_idxs.append(next_entry)

    time_stamps_enter_rwd = df.time[r_entry_idxs]
    time_stamps_exit_rwd = df.time[df.b_code.isin(rwd_taken+sharp_exit)]

    # Calculate time to next pellet eaten or exit
    intervals_rwds = np.zeros_like(time_stamps_enter_rwd.values)
    i=0
    for event_rwd in time_stamps_enter_rwd.values:
        diffs = time_stamps_exit_rwd-event_rwd
        interval = np.min(diffs[diffs>0])
        intervals_rwds[i] = interval/1000
        i=i+1
    r_dwellt_median = np.NaN
    r_dwellt_dist = intervals_rwds
    if ~(np.sum(intervals_rwds)==0):
        r_dwellt_median = np.nanmedian(intervals_rwds)
    return [r_dwellt_median, r_dwellt_dist, no_r_dwellt_median, no_r_dwellt_dist]


def count_rejections(df):
    # This is the old version of counting rejections
    # This will find timestamps and count where all the "clean" rejections occur.
    # By this, we mean the mouse hears offer tone and completely skips the restaurant without entering it.
    no_reward_codes = [17,29,41,53] # no-reward tone codes
    reward_codes = [20,32,44,56] # reward tone codes
    exit_codes = [63,66,69,72] # Exit codes, aka "Sharp" timestamps
    entry_codes = [61,64,67,70] #Entry codes, aka "Sharp"
    accept_codes = [62,65,68,71] #Sharp accept codes
    num_no_reward_tones = len(df.index[df.b_code.isin(no_reward_codes)].values)
    tone_idx = df.index[df.b_code.isin(no_reward_codes+reward_codes)].values
    accept_idx = df.index[df.b_code.isin(accept_codes)].values
    exit_idx = df.index[df.b_code.isin(exit_codes)].values
    entry_idx = df.index[df.b_code.isin(entry_codes)].values
    num_rejects = 0
    reject_ts = []
    for event in tone_idx:
        if (np.any(entry_idx>event))&(np.any(tone_idx>event)):
            next_entry_idx = min(entry_idx[entry_idx>event])
            next_accept_idx = min(accept_idx[accept_idx>event])
            next_exit_idx = min(exit_idx[exit_idx>event])
            next_tone_idx = min(tone_idx[tone_idx>event])
            if ((next_exit_idx<next_accept_idx) & \
                (next_exit_idx<next_entry_idx)):
                num_rejects+=1
                reject_ts = np.append(reject_ts, df.time[event])
    return [num_rejects, num_no_reward_tones, reject_ts]

def collect_rejection_events(df):
    # This is the new version of counting rejections
    # This will find timestamps and count where all the "clean" rejections occur.
    # By this, we mean the mouse hears offer tone and completely skips the restaurant without entering it.
    no_reward_codes = [17,29,41,53] # no-reward tone codes - 0% reward tone
    reward_codes = [20,32,44,56] # reward tone codes - 100% reward tone
    exit_codes = [63,66,69,72] # Exit codes, aka "Sharp" timestamps
    entry_codes = [61,64,67,70] #Entry codes, aka "Sharp"
    accept_codes = [62,65,68,71] #Sharp accept codes
    reject_events = pd.DataFrame(columns=['reject_tone_ts','reject_exit_ts','restaurant'])
    num_no_offer_rejects = 0
    for rr in [1,2,3,4]:
        offer_tone_idx = df.index[df.b_code.isin([reward_codes[rr-1]])].values
        no_offer_tone_idx = df.index[df.b_code.isin([no_reward_codes[rr-1]])].values
        tone_idx = np.append(offer_tone_idx,no_offer_tone_idx)
        accept_idx = df.index[df.b_code.isin([accept_codes[rr-1]])].values
        exit_idx = df.index[df.b_code.isin([exit_codes[rr-1]])].values
        entry_idx = df.index[df.b_code.isin([entry_codes[rr-1]])].values
        for event in tone_idx:
            if (np.any(entry_idx>event)&np.any(exit_idx>event)&np.any(accept_idx>event)): #make sure entry occurs after tone
                next_entry_idx = min(entry_idx[entry_idx>event])
                next_accept_idx = min(accept_idx[accept_idx>event])
                next_exit_idx = min(exit_idx[exit_idx>event])
                #print('next entry: ' + str(next_entry_idx))
                #print('next accept: '+str(next_accept_idx))
                #print('next exit: ' + str(next_exit_idx))
                reject_ts=[]
                if next_exit_idx<next_accept_idx:
                    reject_tone_ts = df.time[event]
                    reject_exit_ts = df.time[next_exit_idx]
                    reject_events = reject_events.append({'reject_tone_ts':reject_tone_ts,'reject_exit_ts':reject_exit_ts,'restaurant':rr},ignore_index=True)
                    if event in no_offer_tone_idx:
                        num_no_offer_rejects+=1
        num_no_offers = len(df.index[df.b_code.isin(no_reward_codes)].values)
        if num_no_offers>0:
            pct_no_offer_rejects = num_no_offer_rejects/num_no_offers
        else:
            pct_no_offer_rejects = 0
    return reject_events, pct_no_offer_rejects

def count_laps(df):
    no_reward_codes = [17,29,41,53] # 0% offer tone codes
    reward_codes = [20,32,44,56] # 100% tone codes
    time_stamps_tone = df.time[df.b_code.isin(no_reward_codes+reward_codes)] # find all instances of tone playing
    num_laps = len(time_stamps_tone)/4 # average out by number of restaurants
    return num_laps
