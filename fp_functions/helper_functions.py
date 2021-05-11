import numpy as np
import pandas as pd
from scipy import signal
import os
import re

def get_data_directories(fp_folder, behavior_folder, mouse_id, day):
    '''
    Get's the csv path to the time stamp, behaviour and FP file for a given mouse and day

    Input:
    mouse_id = RRM00x (String)
    day = xxx (int)

    Return:
    rr_file, fp_file, fpts_file
    '''
    # fp_folder = '/Volumes/Wilbrecht_file_server/Restaurant Row/Data/fp_data/Cohort 3 D1'
    # behavior_folder = '/Volumes/Wilbrecht_file_server/Restaurant Row/Data/rr_data/Cohort 3 D1'

    for file in os.listdir(fp_folder):
        day_check = []
        mouse_id_check = []
        if file.endswith('.csv') & file.startswith('FPTS_'):
            # Pull animal ID from filename
            pattern = 'ID-[^_]+(?=_)'
            match = re.findall(pattern, file)
            if not not match:
                mouse_id_check = match[0][3:]
            # Pull RR Day from filename
            pattern = 'Dayp...'
            match = re.findall(pattern, file)
            if not not match:
                day_check = int(match[0][-3:])
            if ((not not mouse_id_check) & (not not day_check)):
                if (mouse_id == mouse_id_check) & (day == int(day_check)):
                    fpts_file = fp_folder+'/'+file
    for file in os.listdir(fp_folder):
        day_check = []
        mouse_id_check = []
        if file.endswith('.csv') & file.startswith('FP_'):
            # Pull animal ID from filename
            pattern = 'ID-[^_]+(?=_)'
            match = re.findall(pattern, file)
            if not not match:
                mouse_id_check = match[0][3:]
            # Pull RR Day from filename
            pattern = 'Dayp...'
            match = re.findall(pattern, file)
            if not not match:
                day_check = int(match[0][-3:])
            if ((not not mouse_id_check) & (not not day_check)):
                if (mouse_id == mouse_id_check) & (day == int(day_check)):
                    fp_file = fp_folder+'/'+file
    for file in os.listdir(behavior_folder):
        day_check = []
        mouse_id_check = []
        if file.endswith('.csv') & file.startswith('RR_'):
            # Pull animal ID from filename
            pattern = 'ID-[^_]+(?=_)'
            match = re.findall(pattern, file)
            if not not match:
                mouse_id_check = match[0][3:]
            # Pull RR Day from filename
            pattern = 'Dayp...'
            match = re.findall(pattern, file)
            if not not match:
                day_check = int(match[0][-3:])
            if ((not not mouse_id_check) & (not not day_check)):
                if (mouse_id == mouse_id_check) & (day == int(day_check)):
                    rr_file = behavior_folder + '/' + file
    print(fp_file)
    return rr_file, fp_file, fpts_file

def classify_events(df):
    '''
    This will find timestamps and count where all the "clean" rejections occur.
    Clean rejections =  mouse hears offer tone and completely skips the restaurant without entering it.
    '''
    # Create Columns in df
    data_rr = df.assign(event_class=np.ones(len(df))*np.nan)  # Add 'event_class' column
    data_rr = df.assign(offer_tone=np.ones(len(df))*np.nan) #'offer_tone'indicates which tone was given for each event

    # Event Codes
    reward_codes_0 = [17, 29, 41, 53]  # no-reward tone codes
    reward_codes_20 = [18, 30, 42, 54]  # 20pct rewarded tone codesc
    reward_codes_80 = [19, 31, 43, 55]  # 80pct rewarded tone codes
    reward_codes_100 = [20, 32, 44, 56]  # reward tone codes
    reward_taken_codes = [16, 28, 40, 52]  # Pellet taken from dispenser

    servo_open_codes = [1, 3, 5, 7] # Servo arm open = should track with pellets offered
    exit_codes = [63, 66, 69, 72]  # Exit codes, aka "Sharp" timestamps
    entry_codes = [61, 64, 67, 70]  # Entry codes, aka "Sharp"
    accept_codes = [62, 65, 68, 71]  # Sharp accept codes

    # Data frame initialization for holding sorted event timestamps
    reject_events = pd.DataFrame(columns=['reject_tone_ts', 'reject_exit_ts', 'restaurant'])
    num_no_offer_rejects = 0

    accept_and_rewarded_events = pd.DataFrame(columns=['tone_ts', 'accept_ts', 'restaurant'])
    num_accept_rewarded_events = 0

    accept_not_rewarded_events = pd.DataFrame(columns=['tone_ts', 'accept_ts', 'restaurant'])
    num_accept_not_rewarded_events = 0

    quit_events = pd.DataFrame(columns=['tone_ts', 'quit_ts', 'restaurant'])
    num_quit_events = 0

    # Get total number of 0% tone offers
    offer_tone_0_idx = df.index[df.b_code.isin(reward_codes_0)].values
    num_no_offers = len(offer_tone_0_idx)

    dt_reject = [];
    dt_accept = [];

    for rr in [1, 2, 3, 4]:
        offer_tone_100_idx = df.index[df.b_code.isin(
            [reward_codes_100[rr-1]])].values
        offer_tone_80_idx = df.index[df.b_code.isin(
            [reward_codes_80[rr-1]])].values
        offer_tone_20_idx = df.index[df.b_code.isin(
            [reward_codes_20[rr-1]])].values
        offer_tone_0_idx = df.index[df.b_code.isin(
            [reward_codes_0[rr-1]])].values

        tone_idx = np.append(offer_tone_100_idx, offer_tone_80_idx)
        tone_idx = np.append(tone_idx, offer_tone_20_idx)
        tone_idx = np.append(tone_idx, offer_tone_0_idx)

        #find sharp entry, accept and exit codes for each rstrnt
        accept_idx = df.index[df.b_code.isin([accept_codes[rr-1]])].values
        exit_idx = df.index[df.b_code.isin([exit_codes[rr-1]])].values
        entry_idx = df.index[df.b_code.isin([entry_codes[rr-1]])].values
        reward_taken_idx = df.index[df.b_code.isin([reward_taken_codes[rr-1]])].values  # Pellet taken from dispenser
        servo_open_idx = df.index[df.b_code.isin([servo_open_codes[rr-1]])].values # Servo arm open (should track with pellets offered)

        #Print update of pellets revealed vs pellets taken
        print('Pellets Revealed R' + str(rr)+': '+ str(len(servo_open_idx)))
        print('Pellets Eaten R' + str(rr)+': '+ str(len(reward_taken_idx)))

        for event in tone_idx:
            # Determine which offer tone was given for each event
            code = df.b_code[event]
            if code in reward_codes_0:
                tone_prob = 0
            if code in reward_codes_20:
                tone_prob = 20
            if code in reward_codes_80:
                tone_prob = 80
            if code in reward_codes_100:
                tone_prob = 100

            # make sure events (entry, accept, exit, ect.) occurs after tone event (event) (e.g. not last unfinished trial)
            if (np.any(entry_idx > event) & np.any(exit_idx > event)& np.any(accept_idx > event)):
            # if (np.any(entry_idx > event) & np.any(exit_idx > event) & np.any(servo_open_idx > event)):

                next_entry_idx = min(entry_idx[entry_idx > event])
                next_accept_idx = min(accept_idx[accept_idx > event])
                next_exit_idx = min(exit_idx[exit_idx > event])

                # next_pellet_reveal_idx = min(servo_open_idx[servo_open_idx > event])
                # next_reward_taken_idx = min(reward_taken_idx[reward_taken_idx > event])

                # Troubleshooting:
                # print('Tone: '+ str(event))
                # print('Entry: '+str(next_entry_idx))
                # print('Accept: '+str(next_accept_idx))
                # print('Pellet taken: '+str(next_pellet_reveal_idx))
                # print('Exit: '+str(next_exit_idx))

                # Reject Events
                if next_exit_idx < next_accept_idx:
                    # print('Reject')
                    reject_tone_ts = df.time[event]
                    reject_exit_ts = df.time[next_exit_idx]
                    reject_events = reject_events.append(
                        {'reject_tone_ts': reject_tone_ts, 'reject_exit_ts': reject_exit_ts, 'restaurant': rr}, ignore_index=True)
                    if event in offer_tone_0_idx:
                        num_no_offer_rejects += 1
                    data_rr.loc[event, 'event_class'] = 'reject' # tone event
                    data_rr.loc[next_entry_idx, 'event_class'] = 'reject'
                    data_rr.loc[next_accept_idx, 'event_class'] = np.nan
                    data_rr.loc[next_exit_idx, 'event_class'] = 'reject'

                    data_rr.loc[event, 'offer_tone'] = tone_prob
                    data_rr.loc[next_entry_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_accept_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_exit_idx, 'offer_tone'] = tone_prob

                    dt = (data_rr.loc[next_exit_idx, 'time'] - data_rr.loc[next_entry_idx, 'time'])/1000
                    dt_reject.append(dt)
                # Ensure servo_opens
                if (np.any(servo_open_idx > event)):
                    next_pellet_reveal_idx = min(servo_open_idx[servo_open_idx > event])

                    # Quit events
                    if (next_exit_idx > next_accept_idx) & (next_pellet_reveal_idx > next_exit_idx):
                        # print('Quit')
                        quit_tone_ts = df.time[event]
                        quit_event_ts = df.time[next_exit_idx]
                        quit_events = quit_events.append(
                            {'tone_ts': quit_tone_ts, 'quit_ts': quit_event_ts, 'restaurant': rr}, ignore_index=True)
                        num_quit_events += 1
                        data_rr.loc[event, 'event_class'] = 'quit'
                        data_rr.loc[next_entry_idx, 'event_class'] = 'quit'
                        data_rr.loc[next_accept_idx, 'event_class'] = 'quit'
                        data_rr.loc[next_exit_idx, 'event_class'] = 'quit'
                        data_rr.loc[event, 'offer_tone'] = tone_prob
                        data_rr.loc[next_entry_idx, 'offer_tone'] = tone_prob
                        data_rr.loc[next_accept_idx, 'offer_tone'] = tone_prob
                        data_rr.loc[next_exit_idx, 'offer_tone'] = tone_prob

                        # ensure pellet taken
                    if (np.any(reward_taken_idx > event)):
                        next_reward_taken_idx = min(reward_taken_idx[reward_taken_idx > event])

                        # Accept_rewarded events
                        if (next_reward_taken_idx < next_exit_idx):
                        # if (next_pellet_reveal_idx < next_exit_idx):
                            # print('Accept')
                            accept_tone_ts = df.time[event]
                            accept_event_ts = df.time[next_accept_idx]
                            accept_and_rewarded_events = accept_and_rewarded_events.append(
                                {'tone_ts': accept_tone_ts, 'accept_ts': accept_event_ts, 'restaurant': rr}, ignore_index=True)
                            num_accept_rewarded_events += 1
                            data_rr.loc[event, 'event_class'] = 'rewarded'
                            data_rr.loc[next_entry_idx, 'event_class'] = 'rewarded'
                            data_rr.loc[next_accept_idx, 'event_class'] = 'rewarded'
                            data_rr.loc[next_exit_idx, 'event_class'] = 'rewarded'
                            data_rr.loc[next_pellet_reveal_idx,'event_class'] = 'rewarded'
                            data_rr.loc[next_reward_taken_idx,'event_class'] = 'rewarded'

                            data_rr.loc[event, 'offer_tone'] = tone_prob
                            data_rr.loc[next_entry_idx, 'offer_tone'] = tone_prob
                            data_rr.loc[next_accept_idx, 'offer_tone'] = tone_prob
                            data_rr.loc[next_exit_idx, 'offer_tone'] = tone_prob
                            data_rr.loc[next_pellet_reveal_idx,'offer_tone'] = tone_prob
                            data_rr.loc[next_reward_taken_idx,'offer_tone'] = tone_prob

                            dt = (data_rr.loc[next_accept_idx, 'time'] - data_rr.loc[next_entry_idx, 'time'])/1000
                            dt_accept.append(dt)
                # Accept_not_rewarded events
                    # to be determined

            # input('Calculate next event...')
        if num_no_offers != 0:
            print(f"Number of 0% Offer Tone Rejections: {num_no_offer_rejects}")
            pct_no_offer_rejects = num_no_offer_rejects/num_no_offers
        else:
            pct_no_offer_rejects = 0  # Replaced to avoid div by 0 error when there are few events

    # print(f"Percentage of No Offer Rejections: {pct_no_offer_rejects}")
    return (reject_events,
            accept_and_rewarded_events,
            num_accept_rewarded_events,
            quit_events,
            num_quit_events,
            pct_no_offer_rejects, dt_reject, dt_accept,
            data_rr)

def baseline_trace(trace):
    '''
    z-score the FP trace using a median filter
    '''
    frame_interval = 0.025 # collecting data at 40Hz
    kernel = 3

    med_filt = signal.medfilt(trace, 1+int(kernel/frame_interval))  # 3 second long kernel
    trace_backsub = trace-med_filt
    std_trace = np.zeros_like(trace)
    # for i in np.arange(0, len(trace)-int(3/frame_interval)):
    #    std_trace[i] = np.std(trace_backsub[i:i+int(3/frame_interval)])
    # fill zero end pads
    #std_trace[std_trace == 0] = np.mean(std_trace)
    #zscore_trace = trace_backsub/std_trace
    zscore_trace = trace_backsub/(np.std(med_filt))
    return zscore_trace

def grab_fp_traces(alignment, channel, side, condition, data_fp, data_rr, trigger_mode, split):
    '''
    parameters
    alignment: fp traces aligned to this time stamp
        options -> 'offer_tone_x', 'entry', 'accept', 'exit'
            - if looking at condition = reject, need to align to entry
    channel: recording channel for FP
        options -> 'green', 'red', 'control'
    side: hemisphere recording from
        options -> 'left', 'right'
    condition: condition to plot
        options -> 'rewarded', 'reject', 'quit'
    trigger_mode: triggering mode for neurophotometrics system
        options -> 'TRIG1', 'TRIG3'
    split: split fp_traces into different sub-groups
        options -> 'restaurant', 'offer_tone', 'none'
    '''

    # Initialize Event and FP Flag dictionaries
    events = {
        'reward': [16, 28, 40, 52],
        # Servo arm open (should track with pellet taken fro dispenser)
        'servo_open': [1, 3, 5, 7],
        'reward_omission': [15, 27, 39, 51],
        'offer_tone_0': [17, 29, 41, 53],  # no-reward tone codes
        'offer_tone_20': [18, 30, 42, 54],
        'offer_tone_80': [19, 31, 43, 55],  # 80pct rewarded tone codes
        'offer_tone_100': [20, 32, 44, 56],  # reward tone codes
        # DOESNT WORK BECAUSE CYCLING THROUGH ONLY 4 codes of diff restaurants
        'any_offer': [17, 18, 19, 20, 29, 30, 31, 32, 41, 42, 43, 44, 53, 54, 55, 56],
        'exit': [63, 66, 69, 72],
        'entry': [61, 64, 67, 70],
        'accept': [62, 65, 68, 71]}

    fp_flag = { 'TRIG1': {'control':1, 'green':6},
                'TRIG3': {'control':1, 'green':2, 'red':4}}
    fp_flag = fp_flag[trigger_mode]

    if channel == 'control':
        side_channel = side +'_'+ 'green'
    else:
        side_channel = side +'_'+ channel

    # Get FP Signal
    signal_fp = data_fp.get(side_channel)[data_fp.flag == fp_flag[channel]].values
    signal_fp = baseline_trace(signal_fp)    # Baseline and z-score FP trace
    signal_fp_ts = data_fp.time_stamps[data_fp.flag == fp_flag[channel]].values # get TS
    signal_fp_ts = signal_fp_ts[~np.isnan(signal_fp_ts)]  # remove trailing nan

    # Get Alignment Event Codes
    if alignment == 'reject':
        reject_events, pct_no_offer_rejects = collect_rejection_events(data_rr)
        event_ts = reject_events.reject_exit_ts.values # this is the tone time step for rejection events of 0% and 100% offer tone
    else:
        alignment_event_codes = events.get(alignment) # get event codes of alignment events

    # Calculate time window for plotting FP data
    FP_window_sz = 5  # number of seconds before and after event to plot FP data
    frame_interval = np.nanmean(np.diff(signal_fp_ts))/1000 # spacing between frames
    time_window = int(FP_window_sz/frame_interval) # Time window in units of "frames"
    # print(time_window)

    signals_rr = {'R1':[], 'R2':[],'R3':[],'R4':[]} # intialize FP dict
    signals_tone = {'offer_tone_0':np.zeros([0, time_window*2]), 'offer_tone_20':np.zeros([0, time_window*2]),
                    'offer_tone_80': np.zeros([0, time_window*2]), 'offer_tone_100': np.zeros([0, time_window*2])}

    for rr in [1, 2, 3, 4]:
        traces = np.zeros([0, time_window*2])
        if alignment != 'reject':
            alignment_event_code = alignment_event_codes[rr-1]
            alignment_event_idx = data_rr.b_code[data_rr.b_code == alignment_event_code].index.tolist() # get indices of alignment events for single restraunt
            condition_matched = np.array([])

            # Filter for alignment events that match condition: 'reject', 'rewarded', 'quit'
            if np.sum(alignment_event_idx) > 0:
                for event in alignment_event_idx:
                    if (data_rr.event_class[event] == condition):
                        condition_matched = np.append(condition_matched, event)
            condition_event_idx_aligned = condition_matched # indices of events with condition matched
            condition_event_ts_aligned = data_rr.time[condition_event_idx_aligned].values

        for prob in [0, 20, 80, 100]:
            traces_tone = np.zeros([0, time_window*2])
            if len(condition_event_ts_aligned) < 1:
                print(f'Restaurant {rr} has no traces for '+condition+f' condition at probability tone {prob}')
                traces = np.zeros([0, time_window*2]) # avoid error
                continue # skips the for loop

            # Stack Traces of designated window sz for each condition_event_aligned
            for i in np.arange(0, len(condition_event_ts_aligned), 1):
                if data_rr.offer_tone[condition_event_idx_aligned[i]] == prob:
                    ts_rr = condition_event_ts_aligned[i] # Time value of event from computer clock -> rr_data
                    ts_fp = np.argmax(signal_fp_ts > ts_rr)# Index of timestamp that coincides with event timestamp --> fp_data
                    if (ts_fp > time_window) & ((ts_fp+time_window) < len(signal_fp)): #check to make sure within range of array
                        trace = signal_fp[ts_fp - time_window:ts_fp+time_window]
                        traces = np.vstack([traces, trace])
                        traces_tone = np.vstack([traces_tone, trace])

            # Sum Up Events in Prob Tone Array
            # t = np.arange(-time_window, time_window, 1)*frame_interval # time array for plotting
            tone_str = 'offer_tone_'+ str(prob)
            signals_tone[tone_str] = np.concatenate((signals_tone[tone_str],traces_tone), 0)

        # Sum Up Events in Restrnt Array
        rr_str = 'R' + str(rr)
        signals_rr[rr_str] = traces
    t = np.arange(-time_window, time_window, 1)*frame_interval # time array for plotting
    # Signals Array depending on split
    if split == 'none':
        signals = np.concatenate((signals_rr['R1'],signals_rr['R2'],signals_rr['R3'],signals_rr['R4']),0)
    elif split == 'restaurant':
        signals = signals_rr
    elif split == 'offer_tone':
        signals = signals_tone

    return signals, t

def offer_tone_aligned_fp_traces(channel, side, condition, data_fp, data_rr, trigger_mode, split):
    offer_tone_alignments = ['offer_tone_0','offer_tone_20', 'offer_tone_80', 'offer_tone_100']
    time_window = 99

    if split == 'none':
        signals_aligned = np.zeros([0, time_window*2])
    if split == 'restaurant':
        signals_aligned = {'R1':np.zeros([0, time_window*2]), 'R2':np.zeros([0, time_window*2]),
                        'R3': np.zeros([0, time_window*2]), 'R4': np.zeros([0, time_window*2])}
    if split == 'offer_tone':
        signals_aligned = {'offer_tone_0':[], 'offer_tone_20':[],
                        'offer_tone_80': [], 'offer_tone_100': []}
    if split == 'all':
        signals_aligned = {'offer_tone_0':[], 'offer_tone_20':[],
                        'offer_tone_80': [], 'offer_tone_100': []}

    for offer in offer_tone_alignments:

        if split == 'none':
            signals_tone, t = grab_fp_traces(offer, channel, side, condition, data_fp, data_rr, trigger_mode, split)
            signals_aligned = np.vstack([signals_aligned, signals_tone])

        if split == 'restaurant':
            signals_tone, t = grab_fp_traces(offer, channel, side, condition, data_fp, data_rr, trigger_mode, split)
            rest = ['R1','R2', 'R3', 'R4']
            for rr in rest:
                signals_aligned[rr] = np.vstack([signals_aligned[rr], signals_tone[rr]])

        if split == 'offer_tone':
            signals_tone, t = grab_fp_traces(offer, channel, side, condition, data_fp, data_rr, trigger_mode, split)
            signals_aligned[offer] = signals_tone[offer]

        if split == 'all':
            signals_tone, t = grab_fp_traces(offer, channel, side, condition, data_fp, data_rr, trigger_mode, 'restaurant')
            signals_aligned[offer] = signals_tone


    return signals_aligned, t

def grab_fp_traces_all_conditions(alignment, channel, side, data_fp, data_rr, trigger_mode, split):
    conditions = ['rewarded','reject','quit']
    offer_tone_alignments = ['offer_tone_0','offer_tone_20', 'offer_tone_80', 'offer_tone_100']
    time_window = 99

    if split == 'none':
            signals_aligned = np.zeros([0, time_window*2])
    if split == 'restaurant':
        signals_aligned = {'R1':np.zeros([0, time_window*2]), 'R2':np.zeros([0, time_window*2]),
                        'R3': np.zeros([0, time_window*2]), 'R4': np.zeros([0, time_window*2])}
    if split == 'offer_tone':
        signals_aligned = {'offer_tone_0':[], 'offer_tone_20':[],
                        'offer_tone_80': [], 'offer_tone_100': []}
    if split == 'all':
        signals_aligned = {'offer_tone_0':[], 'offer_tone_20':[],
                        'offer_tone_80': [], 'offer_tone_100': []}

    for condition_idx, condition in enumerate(conditions):

        if alignment == 'offer_tone':

            for offer in offer_tone_alignments:

                if split == 'none':
                    signals_tone, t = grab_fp_traces(offer, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, split)
                    signals_aligned = np.vstack([signals_aligned, signals_tone])

                if split == 'restaurant':
                    signals_tone, t = grab_fp_traces(offer, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, split)
                    rest = ['R1','R2', 'R3', 'R4']
                    for rr in rest:
                        signals_aligned[rr] = np.vstack([signals_aligned[rr], signals_tone[rr]])

                if split == 'offer_tone':
                    signals_tone, t = grab_fp_traces(offer, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, split)
                    signals_aligned[offer] = signals_tone[offer]

                if split == 'all':
                    signals_tone, t = grab_fp_traces(offer, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, 'restaurant')
                    signals_aligned[offer] = signals_tone

        if alignment != 'offer_tone':
            if split == 'none':
                signals_tone, t = grab_fp_traces(alignment, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, split)
                signals_aligned = np.vstack([signals_aligned, signals_tone])

            if split == 'restaurant':
                signals_tone, t = grab_fp_traces(alignment, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, split)
                rest = ['R1','R2', 'R3', 'R4']
                for rr in rest:
                    signals_aligned[rr] = np.vstack([signals_aligned[rr], signals_tone[rr]])

            if split == 'offer_tone':
                signals_tone, t = grab_fp_traces(alignment, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, split)
                for offer in offer_tone_alignments:
                    signals_aligned[offer] = signals_tone[offer]

            if split == 'all':
                for offer in offer_tone_alignments:
                    signals_tone, t = grab_fp_traces(offer, channel, side, conditions[condition_idx], data_fp, data_rr, trigger_mode, 'restaurant')
                    signals_aligned[offer] = signals_tone

    return signals_aligned, t
