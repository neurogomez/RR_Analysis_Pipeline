import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import re
import matplotlib as mpl
from matplotlib import rc
import seaborn as sns

sns.set_theme(style="white", context="notebook", palette='deep', font_scale=1.25)

def plot_pellets(df):
    plt.rcParams["figure.figsize"] = (5,3)
    for animal in df.animal_id.unique():
        data = df[df.animal_id.isin([animal])]
        data = data.sort_values(by='day')
        plt.plot(data.day,data.pellets_ph,'o-',alpha=0.5,markersize=16)
    plt.xlabel('Day')
    plt.ylabel('Pellets Eaten per Hour')
    plt.title('Pellets per Hour vs Day')

def plot_iti(df):
    plt.rcParams["figure.figsize"] = (5,3)
    for animal in df.animal_id.unique():
        data = df[df.animal_id.isin([animal])]
        data = data.sort_values(by='day')
        plt.plot(data.day,data.med_ipi,'o-',alpha=0.5,markersize=16)
    plt.xlabel('Day')
    plt.ylabel('Median Inter-Pellet Interval (s)')
    plt.title('Median Interpellet Interval vs Days')

def plot_dwell(df):
    plt.rcParams["figure.figsize"] = (8,6)
    data = df.sort_values(by='day')
    plt.plot(data.day,data.r_dwellt_med,c='b',marker='o',alpha=0.5,markersize=16,label='Reward - 100% Tone')
    plt.plot(data.day,data.no_r_dwellt_med,c='r',marker='v',alpha=0.5,markersize=16,label='No Reward - 0% Tone')
    plt.xlabel('Day')
    plt.ylabel('Median Post Tone Dwell Time (s)')
    plt.legend()
    plt.title('Median Post-Accept Dwell Time vs Days for Rewarded and Non-rewarded Tones')
#     plt.tight_layout()

def plot_rejections(df):
    plt.rcParams["figure.figsize"] = (8,6)
    data = df.sort_values(by='day')
    print('Rejection events per day: '+ str(data.reject_event_count.values))
    plt.plot(data.day,data.reject_accuracy.values,c='b',marker='o',alpha=0.5,markersize=16)
    plt.xlabel('Day')
    plt.ylabel('Reject % for No Offer Tone')
    plt.title('Rejection % for No Offer Tone vs Days')

def plot_laps(df):
    plt.rcParams["figure.figsize"] = (5,3)
    data = df.sort_values(by='day')
    plt.plot(data.day,data.num_laps.values,c='b',marker='o',alpha=0.5,markersize=16)
    plt.xlabel('Day')
    plt.ylabel('Number of Laps')
    plt.ylim([0,100])
    plt.title('Number of Laps vs Days')
