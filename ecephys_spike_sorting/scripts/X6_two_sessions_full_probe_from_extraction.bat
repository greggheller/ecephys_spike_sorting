ECHO off
title Running sorting using two_sessions_full_from_kilosort.py and an input session name
ECHO navigating to code directory
cd C:\Users\svc_neuropix\Documents\GitHub\ecephys_spike_sorting
ECHO THIS SCRIPT PROCESSES 12 PROBES, add any required flags (-ctx, -f. -p, -S for short sort) to the second session name
set /p session_name=Full session name from EXPERIMENT DAY 1: 
set /p session_name2=Full session name from EXPERIMENT DAY 2: 
ECHO activating environment and starting ecephys_spike_sorting\scripts\two_sessions_full_from_kilosort.py
pipenv run python ecephys_spike_sorting\scripts\X6_probe_two_sessions_full_from_kilosort.py %session_name%  %session_name2%
cmd \k



