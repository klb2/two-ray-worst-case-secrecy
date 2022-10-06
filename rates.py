import logging

import numpy as np
import matplotlib.pyplot as plt

from util import export_results, to_decibel, achievable_rate
from two_frequencies import power_eve

LOGGER = logging.getLogger(__name__)

def worst_case_rate_eve(d_min_eve: float, freq: float, bw: float, h_tx: float,
                        h_rx_eve: float):
    _power = power_eve(d_min_eve, 0., freq, h_tx, h_rx_eve)
    _rate_eve = achievable_rate(_power, bw)
    return _rate_eve


def main(d_min_eve: float, freq: float, bw: float, h_tx: float, h_rx: float,
         plot=False, export=False, axs=None):
    df = np.logspace(5, 9, 1000)

    _power_eve = power_eve(d_min_eve, df, freq, h_tx, h_rx)
    rate_eve = achievable_rate(_power_eve, bw)

    _power_eve_approx = power_eve(d_min_eve, 0, freq, h_tx, h_rx)
    rate_eve_lower = achievable_rate(_power_eve_approx, bw)
    rate_eve_lower = np.ones_like(df)*rate_eve_lower

    results = {"df": df,
               "rate": rate_eve/1e6,
               "upper": rate_eve_lower/1e6,
              }

    if plot:
        if axs is None:
            fig, axs = plt.subplots()
        axs.loglog(df, rate_eve, label=f"$f_1=${freq:E} - $R_E$")
        axs.loglog(df, rate_eve_lower, label=f"$f_1=${freq:E} - Approx.")

    if export:
        LOGGER.debug("Exporting single frequency power results.")
        fname = f"rate-eve-{freq:E}-bw{bw:E}-dmin{d_min_eve:.1f}-t{h_tx:.1f}-r{h_rx:.1f}.dat"
        export_results(results, fname)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.)
    parser.add_argument("-r", "--h_rx", type=float, default=1.5)
    parser.add_argument("-f", "--freq", type=float, default=[2.4e9], nargs="+")
    parser.add_argument("-w", "--bw", type=float, default=100e3)
    #parser.add_argument("-df", "--delta_freq", type=float, default=100e6)
    parser.add_argument("-dmin", "--d_min_eve", type=float, default=50.)
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
    fig, axs = plt.subplots()
    freqlist = args.pop("freq")
    for freq in freqlist:
        main(freq=freq, **args, axs=axs)
    axs.set_xlabel("Frequency Spacing $\\Delta f$ [Hz]")
    axs.set_ylabel("Achievable Rate [bit/s]")
    axs.legend()
    plt.show()
