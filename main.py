import numpy as np
import pandas as pd
import os
import re
from behaviour_functions.helper_functions import *
from fp_functions.helper_functions import *
from fp_functions.plotting_fp import *

def load_behavior(path):
    '''
    function for behaviour file collected alone - no FP data
    - different file naming structure: see behaviour notebook for RM011,RM022,RM025
    '''
    results_data = pd.DataFrame(columns=['animal_id','day',\
                                         'pellets_ph','epoch',\
                                         'med_ipi','r_dwellt_med',\
                                         'no_r_dwellt_med',\
                                         'reject_event_count',\
                                         'reject_accuracy',\
                                         'num_laps',\
                                         'total_time'])

    files = [f for f in os.listdir(path) if not f.startswith('.') if f.endswith('.csv')]

    for file in files:
        if file.endswith('.csv'):
            # Load csv
            data = pd.read_csv(path+file,sep=' ',header=None,names = ['time','b_code','none'])
            data = crop_time(data)
            # Pull animal ID from filename
            pattern = 'RRM...' # eg)RRM022
            match = re.findall(pattern,file)
            animal_id = match[0]
            # Pull RR Day from filename
            pattern = 'RR_Day...' #eg) Day012
            match = re.findall(pattern,file)
            day = float(match[0][-3:])
            # Pull epoch from filename
            pattern = 'epoch-.' # eg) epoch-1
            match = re.findall(pattern,file)
            epoch = np.float(match[0][-1])
            # Count number of pellets
            pellet_codes = [16,28,40,52] # reward taken codes
            pellet_loc = data.b_code.isin(pellet_codes)
            num_pellets = np.sum(pellet_loc)
            # Count total time in RR
            total_t = (data.iloc[-1].time/1000 - data.iloc[0].time/1000)/3600 # in hours
            # Calculate inter-pellet interval
            time_stamps = data.time[pellet_loc]
            ipi = np.diff(time_stamps.values)/1000
            if len(ipi)==0:
                med_ipi = np.NaN
            else:
                med_ipi = np.median(ipi)
            # Calculate dwell time after tone
            [r_dwellt_median, r_dwellt_dist, no_r_dwellt_median, no_r_dwellt_dist] = calc_dwell_time_dist(data)
            # Count number of clean reject events
            [reject_events, reject_accuracy]=collect_rejection_events(data)
            # Count number of laps
            num_laps = count_laps(data)
            # Add data to DataFrame
            results_data = results_data.append(
                {'animal_id':animal_id,'day':day,\
                'pellets_ph':num_pellets/total_t,'epoch':epoch,\
                'med_ipi':med_ipi,'r_dwellt_med':r_dwellt_median,\
                'no_r_dwellt_med':no_r_dwellt_median,\
                'reject_event_count':len(reject_events),\
                'reject_accuracy':reject_accuracy,\
                'num_laps':num_laps,\
                'total_time': total_t},\
                ignore_index=True)
    return results_data

def load_behavior_FP(path):
    '''
    function for behaviour file collected with FP data with different file naming convention
    '''
    results_data = pd.DataFrame(columns=['animal_id','day',\
                                         'pellets_ph','epoch',\
                                         'med_ipi','r_dwellt_med',\
                                         'no_r_dwellt_med',\
                                         'reject_event_count',\
                                         'reject_accuracy',\
                                         'num_laps',\
                                         'total_time'])

    files = [f for f in os.listdir(path) if not f.startswith('.') if f.endswith('.csv')]

    for file in files:
        if file.endswith('.csv'):
            # Load csv
            data = pd.read_csv(path+'/'+file,sep=' ',header=None,names = ['time','b_code','none'])
            data = crop_time(data)
            # Pull animal ID from filename
            pattern = 'RRM...' # eg)RRM022
            match = re.findall(pattern,file)
            animal_id = match[0]
            # Pull RR Day from filename
            pattern = 'RR_FP_Dayp...' #eg) Day012
            match = re.findall(pattern,file)
            day = float(match[0][-3:])
            # Pull epoch from filename
            pattern = 'epoch-.' # eg) epoch-1
            match = re.findall(pattern,file)
            epoch = np.float(match[0][-1])
            # Count number of pellets
            pellet_codes = [16,28,40,52] # reward taken codes
            pellet_loc = data.b_code.isin(pellet_codes)
            num_pellets = np.sum(pellet_loc)
            # Count total time in RR
            total_t = (data.iloc[-1].time/1000 - data.iloc[0].time/1000)/3600 # in hours
            # Calculate inter-pellet interval
            time_stamps = data.time[pellet_loc]
            ipi = np.diff(time_stamps.values)/1000
            if len(ipi)==0:
                med_ipi = np.NaN
            else:
                med_ipi = np.median(ipi)
            # Calculate dwell time after tone
            [r_dwellt_median, r_dwellt_dist, no_r_dwellt_median, no_r_dwellt_dist] = calc_dwell_time_dist(data)
            # Count number of clean reject events
            [reject_events, reject_accuracy]=collect_rejection_events(data)
            # Count number of laps
            num_laps = count_laps(data)
            # Add data to DataFrame
            results_data = results_data.append(
                {'animal_id':animal_id,'day':day,\
                'pellets_ph':num_pellets/total_t,'epoch':epoch,\
                'med_ipi':med_ipi,'r_dwellt_med':r_dwellt_median,\
                'no_r_dwellt_med':no_r_dwellt_median,\
                'reject_event_count':len(reject_events),\
                'reject_accuracy':reject_accuracy,\
                'num_laps':num_laps,\
                'total_time': total_t},\
                ignore_index=True)
    return results_data

def get_data_rr(fp_folder, behavior_folder, animal, day): #, alignment, channel,trigger_mode, side, condition, split):
    '''
    main function for grabbing beahviour summary, data_rr and data_fp
    -
    '''

    (rr_file, fp_file, fp_time_stamps) = get_data_directories(fp_folder, behavior_folder, animal, day)

    fp_data = pd.read_csv(fp_file, skiprows=1, names=[
                        'frame', 'cam_time_stamp', 'flag', 'left_red', 'right_red', 'left_green', 'right_green'])
    data_time_stamps = pd.read_csv(fp_time_stamps, names=['time_stamps'])

    data_fp = pd.concat([fp_data, data_time_stamps.time_stamps], axis=1)
    rr_data = pd.read_csv(rr_file, sep=' ', header=None,names=['time', 'b_code', 'none'])

    # Classify events and add class to data_rr df
    (reject_events,
     accept_and_rewarded_events,
     num_accept_rewarded_events,
     quit_events, num_quit_events,
     pct_no_offer_rejects, dt_reject, dt_accept,
     data_rr) = classify_events(rr_data)

    print(f"Percentage of No Offer Rejections: {pct_no_offer_rejects}")
    dt_choice = {'dt_accept':dt_accept, 'dt_reject':dt_reject}

    behaviour_summary = {'reject_events':reject_events,
    'accept_and_rewarded_events':accept_and_rewarded_events,
    'num_accept_rewarded_events':num_accept_rewarded_events,
    'quit_events': quit_events,
    'num_quit_events': num_quit_events,
    'pct_no_offer_rejects': pct_no_offer_rejects,
    'dt_choice': dt_choice}

    # signals, t = grab_fp_traces(alignment, channel, side, condition, data_fp, data_rr, trigger_mode, split)
    # return signals, t, dt_choice
    return behaviour_summary,data_rr, data_fp

def get_fp_aligned_traces(alignment, channel, side, condition, data_fp, data_rr, trigger_mode, baseline_method, split):
    '''
    Calls grab_fp_Traces to perform different splits of the data
    ----
    parameters
    alignment: fp traces aligned to this time stamp
        options -> 'offer_tone_x', 'entry', 'accept', 'exit', 'offer_tone'
            - if looking at condition = reject, need to align to entry
    channel: recording channel for FP
        options -> 'green', 'red', 'control'
    side: hemisphere recording from
        options -> 'left', 'right'
    condition: condition to plot
        options -> 'rewarded', 'reject', 'quit', 'all'
    trigger_mode: triggering mode for neurophotometrics system
        options -> 'TRIG1', 'TRIG3'
    split: split fp_traces into different sub-groups
        options -> 'restaurant', 'offer_tone', 'none', 'all'
    '''

    if condition == 'all':
        signals, t = grab_fp_traces_all_conditions(alignment, channel, side, data_fp, data_rr, trigger_mode,baseline_method, split)
    if condition != 'all':
        if alignment == 'offer_tone':
            signals, t = offer_tone_aligned_fp_traces(channel, side, condition, data_fp, data_rr, trigger_mode,baseline_method, split)
        if alignment != 'offer_tone':
            if split != 'all':
                signals, t = grab_fp_traces(alignment, channel, side, condition, data_fp, data_rr, trigger_mode, baseline_method, split)
            if split == 'all':
                print('ALL split not possible')
    return signals, t

def get_fp_plots_travis(animal, day, alignment, sg, side, condition, split=False, plot_flag='mean'):
    '''
    function for plotting travis' data 
    '''


    fp_folder = '/Volumes/Wilbrecht_file_server/Restaurant Row/Data/fp_data/Cohort 3 D1'
    behavior_folder = '/Volumes/Wilbrecht_file_server/Restaurant Row/Data/rr_data/Cohort 3 D1'

    #animal = 'A2A18DRV'
    #day = 282
    (rr_file, fp_file, fp_time_stamps) = get_data_directories(fp_folder, behavior_folder, animal, day)

    #fp_file = '/Users/travis/Google Drive/Wilbrecht Lab/Restaurant Row/data/Cohort 2 A2A/fp_data/FP_Dayp278_epoch-7_ID-A2A18DRV_2021-01-07T10_40_53.csv'
    #fp_time_stamps = '/Users/travis/Google Drive/Wilbrecht Lab/Restaurant Row/data/Cohort 2 A2A/fp_data/FPTS_Dayp278_epoch-7_ID-A2A18DRV_2021-01-07T10_40_08.csv'
    #rr_file = '/Users/travis/Google Drive/Wilbrecht Lab/Restaurant Row/data/Cohort 2 A2A/rr_data/RR_Dayp278_epoch-7_ID-A2A18DRV2021-01-07T10_40_08.csv'

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
     pct_no_offer_rejects, dt_reject, dt_accept,
     data_rr) = classify_events(rr_data)

    print(f"num of rewarded events: {num_accept_rewarded_events}, num of quit events:{num_quit_events}")

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
    plot_travis_fp(alignment, sg, side, condition, data_fp,
                     data_rr, split, plot_flag)
