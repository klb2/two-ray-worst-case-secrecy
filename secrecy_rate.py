import logging

import numpy as np
from scipy import constants
import matplotlib.pyplot as plt

from model import length_los, length_ref
from two_frequencies import bound_rec_power_two_freq, power_eve
from rates import worst_case_rate_eve
from optimal_frequency_distance import find_optimal_delta_freq
from util import export_results, to_decibel, achievable_rate


LOGGER = logging.getLogger(__name__)

def max_worst_case_sec_rate(d_min_bob: float, d_max_bob: float,
                            d_min_eve: float, freq: float, bw: float,
                            h_tx: float, h_rx_bob: float, h_rx_eve: float,
                            c=constants.c):
    max_power_eve_upper = power_eve(d_min_eve, 0, freq, h_tx, h_rx_eve)
    #rate_eve = achievable_rate(max_power_eve, bw)
    rate_eve = worst_case_rate_eve(d_min_eve, freq, bw, h_tx, h_rx_eve)
    opt_df = find_optimal_delta_freq(d_min_bob, d_max_bob, freq, h_tx, h_rx_bob)
    _power_bob_opt_df = bound_rec_power_two_freq(d_min_bob, d_max_bob, opt_df,
                                                 freq, h_tx, h_rx_bob,
                                                 bound="lower")
    rate_bob_opt_df = achievable_rate(_power_bob_opt_df, bw)
    sec_rate_opt_df = np.maximum(rate_bob_opt_df-rate_eve, 0)
    return sec_rate_opt_df

def main(d_min_bob: float, d_max_bob: float, d_min_eve: float,
         freq: float, bw: float, h_tx: float, h_rx_bob: float, h_rx_eve: float,
         theta: float = 0.5, c=constants.c, plot=False, export=False):
    num_steps = 2000
    df = np.logspace(7, np.log10(freq), num_steps)

    min_power_bob = bound_rec_power_two_freq(d_min_bob, d_max_bob, df, freq,
                                             h_tx, h_rx_bob, bound="lower",
                                             theta=theta)
    rate_bob = achievable_rate(min_power_bob, bw)

    max_power_eve = power_eve(d_min_eve, df, freq, h_tx, h_rx_eve, theta=theta)
    max_power_eve_upper = power_eve(d_min_eve, 0, freq, h_tx, h_rx_eve,
                                    theta=theta)
    #rate_eve = achievable_rate(max_power_eve, bw)
    _rate_eve = achievable_rate(max_power_eve_upper, bw)
    rate_eve = np.ones_like(df) * _rate_eve

    rate_sec = np.maximum(rate_bob-rate_eve, 0)

    results = {
               "df": df,
               "eve": rate_eve,
               "bob": rate_bob,
               "secRate": rate_sec,
              }

    LOGGER.info("Determining the optimal frequency spacing...")
    opt_df = find_optimal_delta_freq(d_min_bob, d_max_bob, freq, h_tx, h_rx_bob,
                                     theta=theta)
    LOGGER.info(f"Optimal frequency spacing: {opt_df:E} Hz")
    _power_bob_opt_df = bound_rec_power_two_freq(d_min_bob, d_max_bob, opt_df,
                                                 freq, h_tx, h_rx_bob,
                                                 bound="lower", theta=theta)
    rate_bob_opt_df = achievable_rate(_power_bob_opt_df, bw)
    sec_rate_opt_df = np.maximum(rate_bob_opt_df-_rate_eve, 0)
    LOGGER.debug(f"Rate Bob at opt. df: {rate_bob_opt_df:E}")
    LOGGER.debug(f"Rate Eve at opt. df: {_rate_eve:E}")
    LOGGER.info(f"Secrecy Rate at opt. df: {sec_rate_opt_df:E}")


    if plot:
        fig, axs = plt.subplots()
        _lim_rate = [1e3, 1e7]
        axs.set_ylim(_lim_rate)
        axs.set_xlim([min(df), max(df)])
        axs.set_xlabel("Delta Freq $\\Delta f$ [Hz]")
        axs.set_ylabel("Rate $R$ [bit/s]")
        axs.loglog(df, rate_bob, label="Worst-case Rate Bob")
        axs.loglog(df, rate_eve, label="Worst-case Rate Eve")
        axs.loglog(df, rate_sec, label="Secrecy Rate")

    if export:
        LOGGER.debug("Exporting results.")
        fname = f"sec-rate-{freq:E}-t{h_tx:.1f}-rB{h_rx_bob:.1f}-rE{h_rx_eve:.1f}-dminB{d_min_bob:.1f}-dmaxB{d_max_bob:.1f}-dminE{d_min_eve:.1f}.dat"
        export_results(results, fname)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.)
    parser.add_argument("-r", "--h_rx_bob", type=float, default=1.5)
    parser.add_argument("-re", "--h_rx_eve", type=float, default=1.5)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-w", "--bw", type=float, default=100e3)
    parser.add_argument("-dmin", "--d_min_bob", type=float, default=20.)
    parser.add_argument("-dmax", "--d_max_bob", type=float, default=30.)
    parser.add_argument("-e", "--d_min_eve", type=float, default=100.)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="Increase output verbosity")
    args = vars(parser.parse_args())
    verb = args.pop("verbosity")
    logging.basicConfig(format="%(asctime)s - %(module)s -- [%(levelname)8s]: %(message)s",
                        handlers=[
                            logging.FileHandler("main.log", encoding="utf-8"),
                            logging.StreamHandler()
                        ])
    loglevel = logging.WARNING - verb*10
    LOGGER.setLevel(loglevel)
    main(**args)
    plt.show()
