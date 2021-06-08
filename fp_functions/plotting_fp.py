# Build DataFrame containing all behavior data
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import re
import matplotlib as mpl
from matplotlib import rc
from fp_functions.helper_functions import *
import seaborn as sns

def plot_trial_avg_FP_aligned(signals, t, split, alignment, side, channel, condition, baseline_method):
    '''
    FP Plotting Function for New Data
    split:  'none': average of all traces
            'seperate_all': split into 16 plots: 4 RR and 4 Offer Tones
            'seperate_restaurant': splits into 4 restaurant plots seperated by 4 offer tones
            'all_offer_tone': 1 plot split into 4 offer tones
            'all_restaurant': 1 plot split into 4 restaurants
            'offer_tone': 4 plots split by offer tones
            'restaurant': 4 plots split by restaurant
            ''
    condition:
    '''

    sns.set_theme(style="white", context="notebook", palette='deep', font_scale=1.25)
    pal = sns.color_palette('deep')
    color_idx = pal.as_hex()

    if baseline_method == 'med_filter':
        y_title = 'FP Signal (a.u)'
    else:
        # signals = signals*1000
        # y_title = 'dF/F * 1000'
        y_title = 'FP Signal Z-Score: (a.u)'

    if split == 'none':
        plt.rcParams["figure.figsize"] = (7, 5)  # (w, h)
        fig, axes = plt.subplots()
        sns.set_theme(font_scale=1)

        mean_trace = np.mean(signals, axis=0)
#         mean_trace = mean_trace - mean_trace[0]
        SEM_trace = np.std(signals, axis=0)/np.sqrt(len(signals))

        axes.plot(t, mean_trace)
        axes.fill_between(t, mean_trace + SEM_trace,mean_trace - SEM_trace, alpha=0.5)
        axes.set_xlabel('Time (s)')
        axes.set_ylabel(y_title)

        ymin, ymax = axes.get_ylim()
        axes.plot([0, 0], [ymin, ymax], '--k')

        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {channel}, Condition: {condition}"
        plt.suptitle(fig_title, fontweight="bold")
        plt.rcParams["figure.figsize"] = (7, 5)  # (w, h)
        plt.tight_layout()

    if split == 'seperate_all':
        sns.set_theme(style="white", context="notebook", palette='deep', font_scale=2.5)
        prob = [0, 20, 80, 100]
        ybounds = 0.4
        pal = sns.color_palette('deep')
        color_idx = pal.as_hex()
        plt.rcParams["figure.figsize"] = (30, 25)  # (w, h)
        fig, axes = plt.subplots(4, 4)
        ax_index = [[(0, 0), (0, 1), (0, 2), (0, 3)],
            [(1, 0), (1, 1), (1, 2), (1, 3)],
           [(2, 0), (2, 1), (2, 2), (2, 3)],
           [(3, 0), (3, 1), (3, 2), (3, 3)]]


        for key in signals:
            prob_idx = list(signals.keys()).index(key)
            for rr in signals[key]:
                rest_idx = list(signals[key].keys()).index(rr)
                mean_trace = np.mean(signals[key][rr], axis=0)
                SEM_trace = np.std(signals[key][rr], axis=0)/np.sqrt(len(signals[key][rr]))

                axes[ax_index[prob_idx][rest_idx]].plot(t, mean_trace, color = color_idx[rest_idx])
                axes[ax_index[prob_idx][rest_idx]].fill_between(t, mean_trace + SEM_trace,mean_trace - SEM_trace, color = color_idx[rest_idx], alpha=0.5)

                axes[ax_index[prob_idx][rest_idx]].set_xlabel('Time (s)')
                axes[ax_index[prob_idx][rest_idx]].set_ylabel(y_title)
                axes[ax_index[prob_idx][rest_idx]].set_title(rr + ' ' + key + '%')
                axes[ax_index[prob_idx][rest_idx]].plot([0, 0], [-ybounds, ybounds], '--k')
                axes[ax_index[prob_idx][rest_idx]].set_ylim(-ybounds, ybounds)

        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {channel}, Condition: {condition}"
        plt.suptitle(fig_title, fontweight="bold")
        plt.tight_layout()

    if split == 'seperate_restaurant':
            plt.rcParams["figure.figsize"] = (12, 10)  # (w, h)
            fig, axes = plt.subplots(2, 2)
            ax_index = [(0, 0), (0, 1), (1, 0), (1, 1)]
            ybounds = 0.6
            prob = [0, 20, 80, 100]

            sns.set_theme(style="white", context="notebook", palette='deep', font_scale=1.25)
            pal = sns.color_palette('deep')
            color_idx = pal.as_hex()

            mean_trace = {'R1':[], 'R2':[],'R3':[],'R4':[]}
            SEM_trace = {'R1':[], 'R2':[],'R3':[],'R4':[]}

            for key in signals:
                prob_idx = list(signals.keys()).index(key)
                for rr in signals[key]:
                    rest_idx = list(signals[key].keys()).index(rr)
                    mean_trace = np.mean(signals[key][rr], axis=0)
                    SEM_trace = np.std(signals[key][rr], axis=0)/np.sqrt(len(signals[key][rr]))

                    axes[ax_index[rest_idx]].plot(t, mean_trace, color = color_idx[prob_idx],label=str(prob[prob_idx]) + '% tone')
                    axes[ax_index[rest_idx]].fill_between(t, mean_trace + SEM_trace,mean_trace - SEM_trace, color = color_idx[prob_idx], alpha=0.25)

                    axes[ax_index[rest_idx]].set_xlabel('Time (s)')
                    axes[ax_index[rest_idx]].set_ylabel(y_title)
                    axes[ax_index[rest_idx]].set_title(rr)
                    axes[ax_index[rest_idx]].legend()
                    axes[ax_index[rest_idx]].plot([0, 0], [-ybounds, ybounds], '--k')
                    axes[ax_index[rest_idx]].set_ylim(-ybounds, ybounds)

    if split == 'all_offer_tone':
        plt.rcParams["figure.figsize"] = (7, 5)  # (w, h)
        fig, axes = plt.subplots()
        sns.set_theme(font_scale=1)
        prob = [0, 20, 80, 100]

        for key in signals:
            prob_idx = list(signals.keys()).index(key)
            mean_trace = np.mean(signals[key], axis=0)
            SEM_trace = np.std(signals[key], axis=0)/np.sqrt(len(signals[key]))

            axes.plot(t, mean_trace, label=str(prob[prob_idx]) + '% tone')
            axes.fill_between(t, mean_trace + SEM_trace,mean_trace - SEM_trace, alpha=0.5)
        axes.set_xlabel('Time (s)')
        axes.set_ylabel(y_title)
        ymin, ymax = axes.get_ylim()
        axes.plot([0, 0], [ymin, ymax], '--k')
        axes.legend()

        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {channel}, Condition: {condition}"
        plt.suptitle(fig_title, fontweight="bold")
        plt.rcParams["figure.figsize"] = (7, 5)  # (w, h)
        plt.tight_layout()

    if split == 'all_restaurant':
        plt.rcParams["figure.figsize"] = (7, 5)  # (w, h)
        fig, axes = plt.subplots()
        sns.set_theme(font_scale=1)
        rest = [1,2,3,4]

        for key in signals:
            rest_idx = list(signals.keys()).index(key)
            mean_trace = np.mean(signals[key], axis=0)
            SEM_trace = np.std(signals[key], axis=0)/np.sqrt(len(signals[key]))

            axes.plot(t, mean_trace, label='R'+ str(rest[rest_idx]))
            axes.fill_between(t, mean_trace + SEM_trace,mean_trace - SEM_trace, alpha=0.5)
        axes.set_xlabel('Time (s)')
        axes.set_ylabel(y_title)
        ymin, ymax = axes.get_ylim()
        axes.plot([0, 0], [ymin, ymax], '--k')
        axes.legend()

        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {channel}, Condition: {condition}"
        plt.suptitle(fig_title, fontweight="bold")
        plt.rcParams["figure.figsize"] = (7, 5)  # (w, h)
        plt.tight_layout()

    if split == 'offer_tone':
        plt.rcParams["figure.figsize"] = (12, 10)  # (w, h)
        fig, axes = plt.subplots(2, 2)
        ax_index = [(0, 0), (0, 1), (1, 0), (1, 1)]
        ybounds = 0.4

        mean_trace = {'offer_tone_0':[], 'offer_tone_20':[],
                    'offer_tone_80':[], 'offer_tone_100': []}
        SEM_trace = {'offer_tone_0':[], 'offer_tone_20':[],
                    'offer_tone_80':[], 'offer_tone_100': []}
        for key in signals:
            offer_tone_idx = list(signals.keys()).index(key)
            mean_trace[key] = np.mean(signals[key], axis=0)
            SEM_trace[key] = np.std(signals[key], axis=0)/np.sqrt(len(signals[key]))

            axes[ax_index[offer_tone_idx]].plot(t, mean_trace[key],color_idx[offer_tone_idx], label=key)
            axes[ax_index[offer_tone_idx]].fill_between(t, mean_trace[key]+SEM_trace[key],
                                          mean_trace[key]-SEM_trace[key], color = color_idx[offer_tone_idx], alpha=0.5)
            axes[ax_index[offer_tone_idx]].set_ylim(-ybounds, ybounds)
            axes[ax_index[offer_tone_idx]].set_xlabel('Time (s)')
            axes[ax_index[offer_tone_idx]].set_ylabel(y_title)
            axes[ax_index[offer_tone_idx]].set_title(key)
#             axes[ax_index[offer_tone_idx]].legend()

            ymin, ymax = axes[ax_index[offer_tone_idx]].get_ylim()
            axes[ax_index[offer_tone_idx]].plot([0, 0], [ymin, ymax], '--k')

        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {channel}, Condition: {condition}"
        plt.suptitle(fig_title, fontweight="bold")
        plt.tight_layout()

    if split == 'restaurant':
        plt.rcParams["figure.figsize"] = (12, 10)  # (w, h)
        fig, axes = plt.subplots(2, 2)
        ax_index = [(0, 0), (0, 1), (1, 0), (1, 1)]
        ybounds = 0.4

        sns.set_theme(style="white", context="notebook", palette='deep', font_scale=1.25)
        pal = sns.color_palette('deep')
        color_idx = pal.as_hex()

        mean_trace = {'R1':[], 'R2':[],'R3':[],'R4':[]}
        SEM_trace = {'R1':[], 'R2':[],'R3':[],'R4':[]}
        for key in signals:
            rr_idx = list(signals.keys()).index(key)
            mean_trace[key] = np.mean(signals[key], axis=0)
            SEM_trace[key] = np.std(signals[key], axis=0)/np.sqrt(len(signals[key]))

            axes[ax_index[rr_idx]].plot(t, mean_trace[key],color_idx[rr_idx], label=key)
            axes[ax_index[rr_idx]].fill_between(t, mean_trace[key]+SEM_trace[key],
                                          mean_trace[key]-SEM_trace[key],color = color_idx[rr_idx], alpha=0.5)
            axes[ax_index[rr_idx]].set_ylim(-ybounds, ybounds)
            axes[ax_index[rr_idx]].set_xlabel('Time (s)')
            axes[ax_index[rr_idx]].set_ylabel(y_title)
            axes[ax_index[rr_idx]].set_title(key)
#             axes[ax_index[rr_idx]].legend()
            ymin, ymax = axes[ax_index[rr_idx]].get_ylim()
            axes[ax_index[rr_idx]].plot([0, 0], [ymin, ymax], '--k')
        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {channel}, Condition: {condition}"
        plt.suptitle(fig_title, fontweight="bold")
        plt.tight_layout()

def plot_travis_fp(alignment, sg, side, condition, data_fp, data_rr, split, plot_flag):
    '''
    FP Plotting Function for plotting Travis's Data
    '''
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
    if alignment == 'reject':
        [num_rejects, num_no_reward_tones,
            reject_ts] = count_rejections(data_rr)
        event_ts = reject_ts
    else:
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
    frame_interval = np.nanmean(np.diff(signal_fp_ts))/1000
    # Time window in units of "frames"
    time_window = int(WINDOW_S/frame_interval)
    sns.set_theme(style="white", context="notebook", palette='deep', font_scale=1.25)

    if split == True:
        fig, axes = plt.subplots(2, 2)
        ax_index = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for rr in [1, 2, 3, 4]:
            if alignment != 'reject':
                event_code = event_codes[rr-1]
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
                #traces = np.zeros([len(event_ts), time_window*2])
                #traces = np.zeros([0, time_window*2])
                if prob == 0:
                    traces = np.zeros([0, time_window*2])
                elif plot_flag!='heatmap':
                    traces = np.zeros([0, time_window*2])
                for i in np.arange(0, len(event_ts), 1):
                    if data_rr.offer_tone[event_idx[i]] == prob:
                        # Time value of event from computer clock
                        ts_rr = event_ts[i]
                        # Index of timestamp that coincides with event timestamp
                        ts_fp = np.argmax(signal_fp_ts > ts_rr)
                        # print('---')
                        #print('Event timestamp: '+str(ts_rr))
                        #print('FP aligned timestamp: '+ str(signal_fp_ts[ts_fp]))
                        #print('Difference: '+str(signal_fp_ts[ts_fp]-ts_rr))
                        if (ts_fp > time_window) & ((ts_fp+time_window) < len(signal_fp)):
                            #trace = signal_fp[ts_fp-time_window:ts_fp+time_window]
                            #traces = np.vstack([traces, trace-trace[0]])
                            trace = signal_fp[ts_fp -
                                              time_window:ts_fp+time_window]
                            traces = np.vstack([traces, trace])
                t = np.arange(-time_window, time_window, 1)*frame_interval
                if np.shape(traces)[0] < 1:
                    # Create zero trace if no events occur
                    traces = np.zeros([1, time_window*2])
                mean_trace = np.mean(traces, axis=0)
                sem_trace = np.std(traces, axis=0)/np.sqrt(len(traces))
                extent = [min(t), max(t), 0, 1]
                if plot_flag == 'heatmap':
                    axes[ax_index[rr-1]].imshow(traces, extent=extent)
                # axes[ax_index[rr-1]].plot(traces.T)
                if plot_flag == 'mean':
                    axes[ax_index[rr-1]].plot(t, mean_trace,
                                              label=str(prob)+'% tone')
                    axes[ax_index[rr-1]].fill_between(t, mean_trace+sem_trace,
                                                      mean_trace-sem_trace, alpha=0.5)
                    axes[ax_index[rr-1]].set_xlabel('Time (s)')
                    axes[ax_index[rr-1]].set_ylabel('FL Signal (a.u)')
                    #axes[ax_index[rr-1]].title(alignment + ' ' + sg + ', R'+str(rr))
                    axes[ax_index[rr-1]].set_title('R'+str(rr))
                    axes[ax_index[rr-1]].legend()
                    # axes[ax_index[rr-1]].set_ylim([-.00004,.00005])
                    # axes[ax_index[rr-1]].set_ylim(ymin,ymax)
            ymin, ymax = axes[ax_index[rr-1]].get_ylim()
            axes[ax_index[rr-1]].plot([0, 0], [ymin, ymax], '--k')

    else:
        fig, axes = plt.subplots()
        plt.rcParams["figure.figsize"] = (7, 5)
        if alignment != 'reject':
            event_idx = np.empty([0,1])
            for code in np.arange(len(event_codes)):
                event_code = event_codes[code]
                event_idx = np.append(event_idx, data_rr.b_code[data_rr.b_code ==
                                                                event_code].index.tolist())
            condition_matched = np.array([])
            # Filter for events that match condition: 'reject', 'rewarded', 'quit'
            if np.sum(event_idx) > 0:
                for event in event_idx:
                    if (data_rr.event_class[event] == condition):
                        condition_matched = np.append(condition_matched, event)
            event_idx = condition_matched
            event_ts = data_rr.time[event_idx].values
        c = 0
        for prob in [0, 20, 80, 100]:
            if len(event_ts) < 1:
                print(f"Restaurant {rr} has no traces for probability tone {prob}")
                continue
            #traces = np.zeros([len(event_ts), time_window*2])
            if prob == 0:
                traces = np.zeros([0, time_window*2])
            elif plot_flag!='heatmap':
                traces = np.zeros([0, time_window*2])
            for i in np.arange(0, len(event_ts), 1):
                if data_rr.offer_tone[event_idx[i]] == prob:
                    # Time value of event from computer clock
                    ts_rr = event_ts[i]
                    # Index of timestamp that coincides with event timestamp
                    ts_fp = np.argmax(signal_fp_ts > ts_rr)
                    # print('---')
                    #print('Event timestamp: '+str(ts_rr))
                    #print('FP aligned timestamp: '+ str(signal_fp_ts[ts_fp]))
                    #print('Difference: '+str(signal_fp_ts[ts_fp]-ts_rr))
                    if (ts_fp > time_window) & ((ts_fp+time_window) < len(signal_fp)):
                        #trace = signal_fp[ts_fp-time_window:ts_fp+time_window]
                        #traces = np.vstack([traces, trace-trace[0]])
                        trace = signal_fp[ts_fp-time_window:ts_fp+time_window]
                        traces = np.vstack([traces, trace])
            t = np.arange(-time_window, time_window, 1)*frame_interval
            if np.shape(traces)[0] < 1:
                # Create zero trace if no events occur
                traces = np.zeros([1, time_window*2])
            mean_trace = np.mean(traces, axis=0)
            sem_trace = np.std(traces, axis=0)/np.sqrt(len(traces))
            extent = [min(t), max(t), 0, 1]
            if plot_flag == 'heatmap':
                axes.imshow(traces, extent=extent)
            color_idx = ['k','r','g','b']
            if plot_flag == 'all':
                axes.plot(t, traces.T,color_idx[c],alpha=0.5)
                c+=1
                print(c)
            if plot_flag == 'mean':
                axes.plot(t, mean_trace,
                          label=str(prob)+'% tone')
                axes.fill_between(t, mean_trace+sem_trace,
                                  mean_trace-sem_trace, alpha=0.5)
                axes.set_xlabel('Time (s)')
                axes.set_ylabel('FL Signal (a.u)')
                #axes[ax_index[rr-1]].title(alignment + ' ' + sg + ', R'+str(rr))
                #axes.set_title('R'+str(rr))
                axes.legend()
                # axes[ax_index[rr-1]].set_ylim([-.00004,.00005])
                # axes[ax_index[rr-1]].set_ylim(ymin,ymax)
        ymin, ymax = axes.get_ylim()
        axes.plot([0, 0], [ymin, ymax], '--k')

        # fig_title = alignment+' '+side+' '+sg+' '+condition
        fig_title = f"Alignment: {alignment}, Hemi: {side}, Signal: {sg}, Condition: {condition}"
        plt.suptitle(fig_title, fontsize=20, fontweight="bold")
        plt.tight_layout()

def plot_dt_hist(dt_choice):
    plt.rcParams["figure.figsize"] = (7, 5)  # (w, h)
    sns.histplot(data=dt_choice)
    sns.set_theme(style="white", context="notebook", palette='deep', font_scale=1.25)
    plt.xlim(0,1)
    plt.title('Time to Accept for Rewarded Trials vs Time to Reject for Reject Trials')
    plt.xlabel('Time (s)')
