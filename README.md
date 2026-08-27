# Restaurant Row: Fibre Photometry and Behaviour Analysis Pipeline

A Python analysis pipeline for **Restaurant Row**, a foraging task used to study decision-making, regret, and their neural correlates. This repo processes raw behavioural event logs from Bonsai and fibre photometry (FP) recordings from mice run on the task in the Wilbrecht Lab (UC Berkeley), turning them into per-session behaviour summaries and trial-aligned FP traces.

## The Restaurant Row paradigm

Restaurant Row was developed to let an animal reveal its own subjective value for a reward against a real opportunity cost, rather than inferring value from a forced-choice trial structure. It was introduced for rats by Steiner & Redish (2014) and later adapted for mice by Sweis, Thomas, & Redish (2018):

> Sweis, B.M., Thomas, M.J., & Redish, A.D. (2018). Mice learn to avoid regret. *PLOS Biology*, 16(6), e2005853. [https://doi.org/10.1371/journal.pbio.2005853](https://doi.org/10.1371/journal.pbio.2005853)

In the original task, a subject runs laps around a square maze with four feeding sites ("restaurants") at the corners, always encountering them in the same order. At each restaurant it passes through an **offer zone**, where a tone pitch signals the ***cost*** of that offer. The subject can choose to enter the **wait zone** and count down for the reward, or to ***skip*** and move to the next restaurant. It can also quit mid-countdown and walk away empty-handed. Each restaurant serves a different flavor, so the animal's willingness to wait reveals how much it values that flavor relative to the cost of the offer, and how that tradeoff changes as time runs out.

### The variant analyzed here

In the Wilbrecht lab task, we keep the four-restaurant, fixed-order structure, but cues **reward probability** rather thatn cost via the pitch of the tone. At each restaurant, an offer tone signals one of four reward levels, each paired with a fixed wait time (from `matlab_pipeline/rr_behaviour_stat.m`):


| Offer tone    | Reward probability | Wait time |
| ------------- | ------------------ | --------- |
| Lowest pitch  | 0%                 | 1 s       |
|               | 20%                | 3 s       |
|               | 80%                | 5 s       |
| Highest pitch | 100%               | 7 s       |


A trial at each restaurant resolves into one of three outcomes, tracked throughout this pipeline (`classify_events` in `fp_functions/helper_functions.py`):

- `reject`: the mouse hears the offer tone and skips the restaurant without entering.
- `quit`: the mouse enters and commits ("accepts"), then exits before the wait period ends and no reward is delivered.
- `rewarded`: the mouse waits out the offer and takes the reward.

Every entry, accept, and exit is logged as a precise "SHARP" timestamp by the Bonsai behavioural control system; the full event code list, including per-restaurant tone, entry, and exit codes, is documented in `files/Bonsai_Event_Codes_RR.xlsx`.

## Repository structure

```
RR_Analysis_Pipeline/
├── README.md
├── main.py                                       # top-level functions: load sessions, classify trials, pull FP traces
├── behaviour_functions/
│   ├── helper_functions.py                       # parse raw event logs into per-session summary stats
│   └── plotting_functions.py                     # plot behaviour metrics (pellets/hr, dwell time, laps, ...) across days
├── fp_functions/
│   ├── helper_functions.py                       # classify_events: label every trial reject/quit/rewarded; pull aligned FP traces
│   ├── plotting_fp.py                             # plot trial-averaged FP traces, split by restaurant/offer/condition
│   └── utils_albert.py                            # shared photometry/dF-F utility library (not authored by me, see Author section)
├── 01_behaviour_summary_RRM003_RRM004.ipynb       # behaviour-only summary for the two FP-recorded mice
├── 02_fp_trace_analysis_RRM003_RRM004.ipynb       # core FP pipeline: classify trials, align traces, plot by condition
├── 03_baseline_method_comparison.ipynb            # compares FP baseline/z-scoring methods on one example session
├── 04_validation_vs_matlab_pipeline.ipynb         # cross-checks Python trial classification against a labmate's MATLAB pipeline
├── 05_behaviour_summary_RRM011_RRM022_RRM025.ipynb # behaviour summary for three mice run without FP
├── matlab_pipeline/                               # a labmate's (Lung-Hao's) alternate MATLAB implementation, kept for reference
├── files/
│   └── Bonsai_Event_Codes_RR.xlsx                 # full codebook: what each numeric event code means
└── Data/                                           # gitignored: private, unpublished data, not tracked in this repo
    ├── RR_Behavior_Data/                          # raw per-session behaviour event logs, by animal
    └── RR_FP_Data/                                # raw per-session FP recordings, by animal
```



### Notebooks

Originally one large notebook covering behaviour, FP traces, baseline-method exploration, and a MATLAB cross-check all in sequence. It's split into five notebooks, each one runs standalone and its purpose is clear from its name:


| #   | Notebook                                          | What it does                                                                                                                                                          |
| --- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `01_behaviour_summary_RRM003_RRM004.ipynb`        | Reward rate, pacing, dwell time, and rejection accuracy across training days for RRM003 and RRM004.                                                                   |
| 2   | `02_fp_trace_analysis_RRM003_RRM004.ipynb`        | The core FP pipeline: classifies trials, pulls FP traces aligned to offer tone / entry / accept / exit, and plots them split by outcome, restaurant, and offer level. |
| 3   | `03_baseline_method_comparison.ipynb`             | Compares the FP baseline-subtraction and z-scoring methods available in `grab_fp_traces` on one example session, to justify the method used in notebook 2.            |
| 4   | `04_validation_vs_matlab_pipeline.ipynb`          | Cross-checks the Python trial classification against Lung-Hao's independent MATLAB implementation, as a correctness check on `classify_events`.                       |
| 5   | `05_behaviour_summary_RRM011_RRM022_RRM025.ipynb` | Same behaviour summary as notebook 1, for three mice that ran the task without FP.                                                                                    |


Each notebook repeats its own imports and data-loading cells (labeled "Setup") rather than depending on state left over from a different notebook, so any one of them can be opened and run on its own.

**Before running:** each notebook's "load sessions for each mouse" cell points at a lab file server path (`/Volumes/Wilbrecht_file_server/...`). Update it to your own path.

## Notes on this repo

- `matlab_pipeline/` **is the prior MatLab version of the pipeline built by a previous lab member, kept for reference and cross-validation.** Notebook 4 in this repo compares my Python `classify_events` against its output as a correctness check.
- `fp_functions/utils_albert.py` **is a shared lab utility library**,I use its dF/F and baseline-correction functions; the rest of the file (e.g. the `ProbSwitch`-task-specific loaders) belongs to a different project and isn't used by this pipeline.
- `Data/` is gitignored: this is private, unpublished mouse data, so it stays local rather than in the repo. The folder structure above documents how it's organized on disk for anyone running the notebooks against their own copy.

## Author

Laura Gomez ([neurogomez](https://github.com/neurogomez))