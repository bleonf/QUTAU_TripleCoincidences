# QUTAU_TripleCOincidences
Script to generate triple coincidence g2 correlation function for single photon source


Generation of triple correlation function from timestamps file obained from qutools qutau module
The inputs for the user are:

    Test: True if the user wants to generate a simple test data generated randomly (no correlation)
    fig:  True if the user wants to save the histogram
    cluster: True if program is running on machine with multiprocessing capabilities
    
    hist_bins: Number of bins to include in histogram
    nrows: Number of rows to use from the qutau data set
    window: time window to use in qutau units (1=81x10^-12 s)
    n: resolution of coincidences (remainder of t/n will be removed)
    
    data_path: path to timestamps file from qutau
To improve speed, the g2 is prepared using collections.Counter and also for repeated runs the script implements pickle saving for the coincidence counter when all numbers are equal, this works mainly for adjusting bin number in histogram.

