# MATLAB Pipeline (reference only)

This folder holds a labmate's (Lung-Hao's) independent MATLAB implementation of Restaurant Row trial classification and behaviour statistics: `rr_behaviour_stat.m` and `RRM004_p158_analysis.m`, plus a thin notebook wrapper (`RR_Behaviour_Analysis-Matlab.ipynb`) for running MATLAB via a Jupyter kernel.

It isn't my own work, and it isn't the pipeline used elsewhere in this repo. It's kept here because `../04_validation_vs_matlab_pipeline.ipynb` cross-checks the Python `classify_events` function against this MATLAB implementation's output, as a correctness check that both pipelines label trial outcomes (reject / quit / rewarded) the same way.

`rr_behaviour_stat.m` documents the task's epoch structure (the training curriculum of offer-tone probabilities available at each stage) and the fixed wait time paired with each offer level; see the main [README](../README.md) for the summarized version of that table.
