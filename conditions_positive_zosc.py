import logging

import numpy as np
from scipy import constants
import matplotlib.pyplot as plt

from util import export_results, to_decibel, achievable_rate
from rates import worst_case_rate_eve
from two_frequencies import sum_power_envelope, power_eve
from secrecy_rate import max_worst_case_sec_rate
from model import length_los, length_ref

LOGGER = logging.getLogger(__name__)


def delta_freq_pi(distance, h_tx, h_rx, c=constants.c):
    _len_los = length_los(distance, h_tx, h_rx)
    _len_ref = length_ref(distance, h_tx, h_rx)
    dw = (c*np.pi)/(_len_ref-_len_los)
    df = dw/(2*np.pi)
    return df

def is_zosc_definitely_positive(d_min_bob: float, d_max_bob: float,
                                d_min_eve: float, freq: float, h_tx: float,
                                h_rx_bob: float, h_rx_eve: float,
                                c=constants.c):
    _df_dmin = delta_freq_pi(d_min_bob, h_tx, h_rx_bob)
    power_bound_bob = sum_power_envelope(d_max_bob, _df_dmin, freq, h_tx,
                                         h_rx_bob, bound="lower")
    power_bound_eve = power_eve(d_min_eve, 0., freq, h_tx, h_rx_eve)
    LOGGER.info(f"LHS:\t{to_decibel(power_bound_bob):.1f}")
    LOGGER.info(f"RHS:\t{to_decibel(power_bound_eve):.1f}")
    return power_bound_bob > power_bound_eve

def is_worst_case_sec_rate_zero(d_max_bob: float, d_min_eve: float,
                                h_tx: float, h_rx_bob: float, h_rx_eve: float,
                                c=constants.c):
    _bob = 1./length_los(d_max_bob, h_tx, h_rx_bob)**2 + 1./length_ref(d_max_bob, h_tx, h_rx_bob)**2
    _eve = 1./length_los(d_min_eve, h_tx, h_rx_eve)**2 + 1./length_ref(d_min_eve, h_tx, h_rx_eve)**2
    LOGGER.info(f"LHS:\t{_bob:E}")
    LOGGER.info(f"RHS:\t{_eve:E}")
    return _bob <= _eve


def main(d_min_bob: float, d_max_bob: float, d_min_eve: float, freq:float,
         bw: float, h_tx: float, h_rx_bob: float, h_rx_eve: float):
    zosc_prob_zero = is_worst_case_sec_rate_zero(d_max_bob, d_min_eve, h_tx,
                                                 h_rx_bob, h_rx_eve)
    LOGGER.info(f"ZOSC is probably zero: {zosc_prob_zero}")

    zosc_def_positive = is_zosc_definitely_positive(d_min_bob, d_max_bob,
                                                    d_min_eve, freq, h_tx,
                                                    h_rx_bob, h_rx_eve)
    LOGGER.info(f"ZOSC is definitely positive: {zosc_def_positive}")

    actual_zosc = max_worst_case_sec_rate(d_min_bob, d_max_bob, d_min_eve,
                                          freq, bw, h_tx, h_rx_bob, h_rx_eve)
    LOGGER.info(f"Actual ZOSC: {actual_zosc:E}")


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
    parser.add_argument("--d_min_eve", type=float, default=50.)
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
