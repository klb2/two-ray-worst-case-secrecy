#!/bin/sh

# This repository is accompanying the paper "Frequency Diversity for
# Ultra-Reliable and Secure Communications in Sub-THz Two-Ray Scenarios" (K.-L.
# Besser, E. Jorswieck, J. Coon, IEEE ICC 2023. doi:10.1109/ICC45041.2023.10279098).
#
# Copyright (C) 2022 Karl-Ludwig Besser
# License: GPLv3

FREQ="2.4e9"
DF="250e6"
HTX="10"
HRX="1.5"
BW="100e3"

echo "Figure 3: Total sum receive power"
python3 two_frequencies.py -v -f "$FREQ" -df "$DF" -t "$HTX" -r "$HRX" --plot --export

echo "Figure 4: Worst-case achievable rate for Eve"
python3 rates.py -v -f "500e6" "1e9" "2.4e9" -w "$BW" -t "$HTX" -r "$HRX" --plot --export

echo "Figure 5: Secrecy rate over frequency spacing (Example 3)"
python3 secrecy_rate.py -v -t "$HTX" -r "$HRX" -re "$HRX" -f "$FREQ" -w "$BW" -dmin 20 -dmax 30 --d_min_eve 100 --plot --export

echo "Example 4: Higher Frequency Example"
python3 secrecy_rate.py -v -t "5" -r "1" -re "1.5" -dmin 40 -dmax 50 --d_min_eve 100 -f "30e9" -w "100e3" --plot


echo "Example 5: Conditions for a positive ZOSC"
python3 conditions_positive_zosc.py -v -f "$FREQ" -w "$BW" -t "$HTX" -r "$HRX" -re "$HRX" -dmin 20 -dmax 30 --d_min_eve 100
python3 conditions_positive_zosc.py -v -f "$FREQ" -w "$BW" -t "$HTX" -r "$HRX" -re "$HRX" -dmin 20 -dmax 30 --d_min_eve 50
python3 conditions_positive_zosc.py -v -f "$FREQ" -w "$BW" -t "$HTX" -r "$HRX" -re "$HRX" -dmin 20 -dmax 30 --d_min_eve 20
