# import jplotprefs
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import re
import matplotlib as mpl
from matplotlib import rc
from scipy import signal

rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
mpl.rcParams['font.family'] = "sans-serif"
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
# rc('text', usetex=False)
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
plt.rcParams.update({'font.size': 10})
plt.rcParams["figure.figsize"] = (8, 5)  # (w, h)


def get_data_directories(mouse_id, day):
    fp_folder = '/Volumes/Wilbrecht_file_server/Restaurant Row/Data/fp_data/Cohort 3 D1'
    behavior_folder = '/Volumes/Wilbrecht_file_server/Restaurant Row/Data/rr_data/Cohort 3 D1'

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
                    fpts_file = fp_folder + '/' + file
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
                    fp_file = fp_folder + '/' + file
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


def get_fp_plots(animal, day, alignment, sg, side, condition, split=False, plot_flag='mean'):
    # animal = 'A2A18DRV'
    # day = 282
    (rr_file, fp_file, fp_time_stamps) = get_data_directories(animal, day)

    # fp_file = '/Users/travis/Google Drive/Wilbrecht Lab/Restaurant Row/data/Cohort 2 A2A/fp_data/FP_Dayp278_epoch-7_ID-A2A18DRV_2021-01-07T10_40_53.csv'
    # fp_time_stamps = '/Users/travis/Google Drive/Wilbrecht Lab/Restaurant Row/data/Cohort 2 A2A/fp_data/FPTS_Dayp278_epoch-7_ID-A2A18DRV_2021-01-07T10_40_08.csv'
    # rr_file = '/Users/travis/Google Drive/Wilbrecht Lab/Restaurant Row/data/Cohort 2 A2A/rr_data/RR_Dayp278_epoch-7_ID-A2A18DRV2021-01-07T10_40_08.csv'

    data = pd.read_csv(fp_file, skiprows=1, names=[
        'frame', 'cam_time_stamp', 'flag', 'right_red', 'left_red', 'right_green', 'left_green'])
    data_time_stamps = pd.read_csv(
        fp_time_stamps, names=['time_stamps'])

    data_fp = pd.concat([data, data_time_stamps.time_stamps], axis=1)
    rr_data = pd.read_csv(rr_file, sep=' ', header=None,
                          names=['time', 'b_code', 'none'])

    # Classify events and add class to data_rr df
    (reject_events,
     accept_and_rewarded_events,
     num_accept_rewarded_events,
     quit_events, num_quit_events,
     pct_no_offer_rejects,
     data_rr) = classify_events(rr_data)
    '''
    # Green signal
    right_green_fp = data_fp.right_green[data_fp.flag == 2].values
    right_green_fp_ts = data_fp.time_stamps[data_fp.flag == 2].values
    left_green_fp = data_fp.left_green[data_fp.flag == 2].values
    left_green_fp_ts = data_fp.time_stamps[data_fp.flag == 2].values
    # Red signal
    right_red_fp = data_fp.right_red[data_fp.flag == 4].values
    right_red_fp_ts = data_fp.time_stamps[data_fp.flag == 4].values
    left_red_fp = data_fp.left_red[data_fp.flag == 4].values
    left_red_fp_ts = data_fp.time_stamps[data_fp.flag == 4].values
    # Control signal (415nm)
    right_control_fp = data_fp.right_green[data_fp.flag == 1].values
    right_control_fp_ts = data_fp.time_stamps[data_fp.flag == 1].values
    left_control_fp = data_fp.left_green[data_fp.flag == 1].values
    left_control_fp_ts = data_fp.time_stamps[data_fp.flag == 1].values
    '''

    # condition can be "reject","rewarded" or "quit"
    plot_fp_data(alignment, sg, side, condition, data_fp,
                     data_rr, split, plot_flag)


def plot_fp_data(alignment, sg, side, condition, data_fp, data_rr, split, plot_flag):
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
        'accept': [62, 65, 68, 71]
    }
    event_codes = events.get(alignment)

    if side == 'left':
        if sg == 'green':
            signal_fp = data_fp.left_green[data_fp.flag == 2].values
            # Baseline and z-score FP trace
            signal_fp = baseline_trace(signal_fp)
            signal_fp_ts = data_fp.time_stamps[data_fp.flag == 2].values
            signal_fp_ts = signal_fp_ts[~np.isnan(
                signal_fp_ts)]  # remove trailing nan
        elif sg == 'red':
            signal_fp = data_fp.left_red[data_fp.flag == 4].values
            signal_fp = baseline_trace(signal_fp)
            signal_fp_ts = data_fp.time_stamps[data_fp.flag == 4].values
            signal_fp_ts = signal_fp_ts[~np.isnan(
                signal_fp_ts)]  # remove trailing nan
        elif sg == 'control':
            signal_fp = data_fp.left_green[data_fp.flag == 1].values
            signal_fp = baseline_trace(signal_fp)
            signal_fp_ts = data_fp.time_stamps[data_fp.flag == 1].values
            signal_fp_ts = signal_fp_ts[~np.isnan(
                signal_fp_ts)]  # remove trailing nan
    if side == 'right':
        if sg == 'green':
            signal_fp = data_fp.right_green[data_fp.flag == 2].values
            signal_fp = baseline_trace(signal_fp)
            signal_fp_ts = data_fp.time_stamps[data_fp.flag == 2].values
            signal_fp_ts = signal_fp_ts[~np.isnan(
                signal_fp_ts)]  # remove trailing nan
        elif sg == 'red':
            signal_fp = data_fp.right_red[data_fp.flag == 4].values
            signal_fp = baseline_trace(signal_fp)
            signal_fp_ts = data_fp.time_stamps[data_fp.flag == 4].values
            signal_fp_ts = signal_fp_ts[~np.isnan(
                signal_fp_ts)]  # remove trailing nan
        elif sg == 'control':
            signal_fp = data_fp.right_green[data_fp.flag == 1].values
            signal_fp = baseline_trace(signal_fp)
            signal_fp_ts = data_fp.time_stamps[data_fp.flag == 1].values
            signal_fp_ts = signal_fp_ts[~np.isnan(
                signal_fp_ts)]  # remove trailing nan

    # Calculate time window for plotting FP data
    WINDOW_S = 3  # number of seconds before and after event to plot FP data
    frame_interval = np.nanmedian(np.diff(signal_fp_ts[0:100])) / 1000
    # Time window in units of "frames"
    time_window = int(WINDOW_S / frame_interval)
    # Choose to divide plots by restaurant
    if split == True:
        fig, axes = plt.subplots(2, 2)
        ax_index = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for rr in [1, 2, 3, 4]:
            if alignment != 'reject':
                event_code = event_codes[rr - 1]
                event_idx = data_rr.b_code[data_rr.b_code ==
                                           event_code].index.tolist()
                condition_matched = np.array([])
                # Filter for events that match condition: 'reject', 'rewarded', 'quit'
                if np.sum(event_idx) > 0:
                    for event in event_idx:
                        if (data_rr.event_class[event] == condition):
                            condition_matched = np.append(
                                condition_matched, event)
                event_idx = condition_matched
                event_ts = data_rr.time[event_idx].values

            for prob in [0, 20, 80, 100]:
                if len(event_ts) < 1:
                    print(
                        f"Restaurant {rr} has no traces for probability tone {prob}")
                    continue
                # traces = np.zeros([len(event_ts), time_window*2])
                # traces = np.zeros([0, time_window*2])
                if prob == 0:
                    traces = np.zeros([0, time_window * 2])
                elif plot_flag != 'heatmap':
                    traces = np.zeros([0, time_window * 2])
                for i in np.arange(0, len(event_ts), 1):
                    if data_rr.offer_tone[event_idx[i]] == prob:
                        # Time value of event from computer clock
                        ts_rr = event_ts[i]
                        # Index of timestamp that coincides with event timestamp
                        ts_fp = np.argmax(signal_fp_ts > ts_rr)
                        # print('---')
                        # print('Event timestamp: '+str(ts_rr))
                        # print('FP aligned timestamp: '+ str(signal_fp_ts[ts_fp]))
                        # print('Difference: '+str(signal_fp_ts[ts_fp]-ts_rr))
                        if (ts_fp > time_window) & ((ts_fp + time_window) < len(signal_fp)):
                            # trace = signal_fp[ts_fp-time_window:ts_fp+time_window]
                            # traces = np.vstack([traces, trace-trace[0]])
                            trace = signal_fp[ts_fp -
                                              time_window:ts_fp + time_window]
                            traces = np.vstack([traces, trace])
                t = np.arange(-time_window, time_window, 1) * frame_interval
                if np.shape(traces)[0] < 1:
                    # Create zero trace if no events occur
                    traces = np.zeros([1, time_window * 2])
                mean_trace = np.mean(traces, axis=0)
                sem_trace = np.std(traces, axis=0) / np.sqrt(len(traces))
                extent = [min(t), max(t), 0, 1]
                if plot_flag == 'heatmap':
                    axes[ax_index[rr - 1]].imshow(traces, extent=extent)
                if plot_flag == 'all':
                    axes[ax_index[rr-1]].plot(t,traces.T)
                if plot_flag == 'mean':
                    axes[ax_index[rr - 1]].plot(t, mean_trace,
                                                label=str(prob) + '% tone')
                    axes[ax_index[rr - 1]].fill_between(t, mean_trace + sem_trace,
                                                        mean_trace - sem_trace, alpha=0.5)
                    axes[ax_index[rr - 1]].set_xlabel('Time (s)')
                    axes[ax_index[rr - 1]].set_ylabel('FL Signal (a.u)')
                    axes[ax_index[rr - 1]].set_title('R' + str(rr))
                    axes[ax_index[rr - 1]].legend()
            ymin, ymax = axes[ax_index[rr - 1]].get_ylim()
            axes[ax_index[rr - 1]].plot([0, 0], [ymin, ymax], '--k')
    # Combine data from all restaurants
    else:
        fig, axes = plt.subplots()
        event_idx = np.empty([0, 1])
        for code in np.arange(len(event_codes)):
            event_code = event_codes[code]
            event_idx = np.append(event_idx, data_rr.b_code[data_rr.b_code ==
                                                            event_code].index.tolist())
        condition_matched = np.array([])
        # Filter for events that match condition: 'reject', 'rewarded', 'quit', 'any'
        if condition != 'any':
            if np.sum(event_idx) > 0:
                for event in event_idx:
                    if data_rr.event_class[event] == condition:
                        condition_matched = np.append(condition_matched, event)
            event_idx = condition_matched
        event_ts = data_rr.time[event_idx].values
        c = 0
        event_counts = []
        for prob in [0, 20, 80, 100]:
            event_count = 0
            if len(event_ts) < 1:
                print(
                    f"No events for probability tone {prob}")
                continue
            if prob == 0:
                traces = np.zeros([0, time_window * 2])
            elif plot_flag != 'heatmap': #Prevent overwriting of heatmap for each prob
                traces = np.zeros([0, time_window * 2])
            for i in np.arange(0, len(event_ts), 1):
                if data_rr.offer_tone[event_idx[i]] == prob:
                    # Time value of event from computer clock
                    ts_rr = event_ts[i]
                    # Index of timestamp that coincides with event timestamp
                    ts_fp = np.argmax(signal_fp_ts > ts_rr)
                    if (ts_fp > time_window) & ((ts_fp + time_window) < len(signal_fp)):
                        # trace = signal_fp[ts_fp-time_window:ts_fp+time_window]
                        # traces = np.vstack([traces, trace-trace[0]])
                        trace = signal_fp[ts_fp - time_window:ts_fp + time_window]
                        traces = np.vstack([traces, trace])
                        event_count += 1
            event_counts = np.append(event_counts, event_count)
            t = np.arange(-time_window, time_window, 1) * frame_interval
            if np.shape(traces)[0] < 1:
                # Create zero trace if no events occur
                traces = np.zeros([1, time_window * 2])
            mean_trace = np.mean(traces, axis=0)
            mean_trace = mean_trace - mean_trace[0]
            sem_trace = np.std(traces, axis=0) / np.sqrt(len(traces))
            extent = [min(t), max(t), 0, 1]
            if plot_flag == 'heatmap':
                axes.imshow(traces, extent=extent)
            color_idx = ['k', 'r', 'g', 'b']
            if plot_flag == 'all':
                axes.plot(t, traces.T, color_idx[c], alpha=0.5)
                c += 1
                print(c)
            if plot_flag == 'mean':
                axes.plot(t, mean_trace,
                          label=str(prob) + '% tone')
                axes.fill_between(t, mean_trace + sem_trace,
                                  mean_trace - sem_trace, alpha=0.5)
                axes.set_xlabel('Time (s)')
                axes.set_ylabel('FL Signal (a.u)')
                axes.legend()
        ymin, ymax = axes.get_ylim()
        axes.plot([0, 0], [ymin, ymax], '--k')

        fig_title = alignment + ' ' + side + ' ' + sg + ' ' + condition
        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {sg}, Condition: {condition}. \n Event Counts: P0: {event_counts[0]:.0f}, " \
                    f"P20: {event_counts[1]:.0f},  " \
                    f"P80: {event_counts[2]:.0f}, " \
                    f"P100: {event_counts[3]:.0f}"
        plt.suptitle(fig_title)
        plt.tight_layout()


def classify_events(df):
    # This will find timestamps and count where all the "clean" rejections occur.
    # By this, we mean the mouse hears offer tone and completely skips the restaurant without entering it.
    data_rr = df.assign(event_class=np.ones(len(df)) *
                                    np.nan)  # Add 'event_class' column
    # Add 'offer_tone' column to indicate which tone was given for each event
    data_rr = df.assign(offer_tone=np.ones(len(df)) * np.nan)
    reward_codes_0 = [17, 29, 41, 53]  # no-reward tone codes
    reward_codes_20 = [18, 30, 42, 54]  # 20pct rewarded tone codesc
    reward_codes_80 = [19, 31, 43, 55]  # 80pct rewarded tone codes
    reward_codes_100 = [20, 32, 44, 56]  # reward tone codes
    reward_taken_codes = [16, 28, 40, 52]  # Pellet taken from dispenser
    # Servo arm open (should track with pellet taken fro dispenser)
    servo_open_codes = [1, 3, 5, 7]
    exit_codes = [63, 66, 69, 72]  # Exit codes, aka "Sharp" timestamps
    entry_codes = [61, 64, 67, 70]  # Entry codes, aka "Sharp"
    accept_codes = [62, 65, 68, 71]  # Sharp accept codes
    # Data frame initialization for holding sorted event timestamps
    reject_events = pd.DataFrame(
        columns=['reject_tone_ts', 'reject_exit_ts', 'restaurant'])
    num_no_offer_rejects = 0
    accept_and_rewarded_events = pd.DataFrame(
        columns=['tone_ts', 'accept_ts', 'restaurant'])
    num_accept_rewarded_events = 0
    accept_not_rewarded_events = pd.DataFrame(
        columns=['tone_ts', 'accept_ts', 'restaurant'])
    num_accept_not_rewarded_events = 0
    quit_events = pd.DataFrame(columns=['tone_ts', 'quit_ts', 'restaurant'])
    num_quit_events = 0

    for rr in [1, 2, 3, 4]:
        offer_tone_100_idx = df.index[df.b_code.isin(
            [reward_codes_100[rr - 1]])].values
        offer_tone_80_idx = df.index[df.b_code.isin(
            [reward_codes_80[rr - 1]])].values
        offer_tone_20_idx = df.index[df.b_code.isin(
            [reward_codes_20[rr - 1]])].values
        offer_tone_0_idx = df.index[df.b_code.isin(
            [reward_codes_0[rr - 1]])].values
        num_no_offers = len(offer_tone_0_idx)
        tone_idx = np.append(offer_tone_100_idx, offer_tone_80_idx)
        tone_idx = np.append(tone_idx, offer_tone_20_idx)
        tone_idx = np.append(tone_idx, offer_tone_0_idx)
        accept_idx = df.index[df.b_code.isin([accept_codes[rr - 1]])].values
        exit_idx = df.index[df.b_code.isin([exit_codes[rr - 1]])].values
        entry_idx = df.index[df.b_code.isin([entry_codes[rr - 1]])].values
        reward_taken_idx = df.index[df.b_code.isin(
            [reward_taken_codes[rr - 1]])].values  # Pellet taken from dispenser
        # Servo arm open (should track with pellet taken fro dispenser)
        servo_open_idx = df.index[df.b_code.isin(
            [servo_open_codes[rr - 1]])].values
        print('Pellets Revealed R' + str(rr) + ': ' + str(len(servo_open_idx)))
        print('Pellets Eaten R' + str(rr) + ': ' + str(len(reward_taken_idx)))
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
            # make sure events occurs after tone (e.g. not last unfinished trial)
            if (np.any(entry_idx > event) & np.any(exit_idx > event) & np.any(servo_open_idx > event)):
                next_entry_idx = min(entry_idx[entry_idx > event])
                next_accept_idx = min(accept_idx[accept_idx > event])
                next_exit_idx = min(exit_idx[exit_idx > event])
                next_pellet_reveal_idx = min(
                    servo_open_idx[servo_open_idx > event])
                # Reject Events
                if next_exit_idx < next_accept_idx:
                    # print('Reject')
                    reject_tone_ts = df.time[event]
                    reject_exit_ts = df.time[next_exit_idx]
                    reject_events = reject_events.append(
                        {'reject_tone_ts': reject_tone_ts, 'reject_exit_ts': reject_exit_ts, 'restaurant': rr},
                        ignore_index=True)
                    if event in offer_tone_0_idx:
                        num_no_offer_rejects += 1
                    data_rr.loc[event, 'event_class'] = 'reject'
                    data_rr.loc[next_entry_idx, 'event_class'] = 'reject'
                    data_rr.loc[next_accept_idx, 'event_class'] = np.nan
                    data_rr.loc[next_exit_idx, 'event_class'] = 'reject'
                    data_rr.loc[event, 'offer_tone'] = tone_prob
                    data_rr.loc[next_entry_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_accept_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_exit_idx, 'offer_tone'] = tone_prob

                # Accept_rewarded events
                if (next_pellet_reveal_idx < next_exit_idx):
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
                    data_rr.loc[next_pellet_reveal_idx,
                                'event_class'] = 'rewarded'
                    data_rr.loc[event, 'offer_tone'] = tone_prob
                    data_rr.loc[next_entry_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_accept_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_exit_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_pellet_reveal_idx,
                                'offer_tone'] = tone_prob
                # Accept_not_rewareded events

                # Quit events
                if (next_exit_idx > next_accept_idx) & (next_pellet_reveal_idx > next_exit_idx):
                    # print('Quit')
                    quit_tone_ts = df.time[event]
                    quit_event_ts = df.time[next_exit_idx]
                    quit_events = quit_events.append(
                        {'tone_ts': quit_tone_ts, 'quit_ts': quit_event_ts, 'restaurant': rr}, ignore_index=True)
                    num_quit_events += 1
                    data_rr.loc[event, 'event_class'] = 'quit'
                    # print(data_rr.event_class[event])
                    data_rr.loc[next_entry_idx, 'event_class'] = 'quit'
                    data_rr.loc[next_accept_idx, 'event_class'] = 'quit'
                    data_rr.loc[next_exit_idx, 'event_class'] = 'quit'
                    data_rr.loc[event, 'offer_tone'] = tone_prob
                    data_rr.loc[next_entry_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_accept_idx, 'offer_tone'] = tone_prob
                    data_rr.loc[next_exit_idx, 'offer_tone'] = tone_prob

            # input('Calculate next event...')
        # pct_no_offer_rejects = num_no_offer_rejects/num_no_offers
        pct_no_offer_rejects = 0  # Replaced to avoid div by 0 error when there are few events
    return (reject_events,
            accept_and_rewarded_events,
            num_accept_rewarded_events,
            quit_events,
            num_quit_events,
            pct_no_offer_rejects,
            data_rr)


def baseline_trace(trace):
    frame_interval = 0.025
    med_filt = signal.medfilt(
        trace, 1 + int(3 / frame_interval))  # 3 second long kernel
    trace_backsub = trace - med_filt
    std_trace = np.zeros_like(trace)
    zscore_trace = trace_backsub / (np.std(trace_backsub))
    return zscore_trace
