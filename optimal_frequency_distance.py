import logging

import numpy as np
from scipy import constants
from scipy import optimize
import matplotlib.pyplot as plt

from single_frequency import rec_power, min_rec_power_single_freq, crit_dist
from two_frequencies import sum_power_envelope, delta_freq_peak_approximation
from util import to_decibel, export_results


LOGGER = logging.getLogger(__name__)

def sum_power_d1(delta_freq, freq, h_tx, h_rx, theta=0.5, c=constants.c, power_tx=1):
    d1 = crit_dist(delta_freq, h_tx, h_rx, k=1)
    return sum_power_envelope(d1, delta_freq, freq, h_tx, h_rx, theta=theta)


def find_optimal_delta_freq(d_min: float, d_max: float, freq: float, 
                            h_tx: float, h_rx: float, theta: float = 0.5,
                            c: float = constants.speed_of_light):
    if d_max <= d_min:
        raise ValueError("The maximum distance needs to be larger than the minimum distance.")

    # Preparation
    _df_pi_dmin, _df_2pi_dmin = delta_freq_peak_approximation(d_min, h_tx, h_rx)
    _df_pi_dmax, _df_2pi_dmax = delta_freq_peak_approximation(d_max, h_tx, h_rx)

    power_dmax_max = sum_power_envelope(d_max, _df_pi_dmax, freq, h_tx, h_rx,
                                        theta=theta)
    if _df_pi_dmax > _df_2pi_dmin:
        g_dmax_max = sum_power_d1(_df_pi_dmax, freq, h_tx, h_rx, theta=theta)
    else:
        g_dmax_max = sum_power_envelope(d_min, _df_pi_dmax, freq, h_tx, h_rx,
                                        theta=theta)
    
    # Branch 1: No intersection
    if power_dmax_max < g_dmax_max:
        LOGGER.warn("No intersection between P_r(dmax) and g. Using approximation")
        opt_df = _df_pi_dmax
        return opt_df

    # Branch 2: Intersection
    power_dmax_dmin = sum_power_envelope(d_max, _df_2pi_dmin, freq, h_tx, h_rx,
                                         theta=theta)
    power_dmin_min = sum_power_envelope(d_min, _df_2pi_dmin, freq, h_tx, h_rx,
                                        theta=theta)
    if power_dmax_dmin > power_dmin_min:
        _bounds = [np.log10(_df_pi_dmin), np.log10(_df_2pi_dmin)]
        g_min = lambda x: sum_power_envelope(d_min, 10**x, freq, h_tx, h_rx,
                                             theta=theta)
    else:
        _bounds = [np.log10(_df_2pi_dmin), np.log10(_df_2pi_dmax)]
        g_min = lambda x: sum_power_d1(10**x, freq, h_tx, h_rx, theta=theta)
    p_max = lambda x: sum_power_envelope(d_max, 10**x, freq, h_tx, h_rx,
                                         theta=theta)
    func_opt = lambda x: np.abs(np.log(p_max(x))-np.log(g_min(x)))
    opt = optimize.minimize(func_opt, x0=np.mean(_bounds),
                            bounds=optimize.Bounds(*_bounds))
    opt_df = 10**opt.x[0]
    return opt_df

def main_optimal_frequency_distance(d_min: float, d_max: float, freq: float, 
                                    h_tx: float, h_rx: float,
                                    c: float = constants.speed_of_light,
                                    plot=False, export=False):

    distance = np.logspace(np.log10(d_min)-.1, np.log10(d_max)+.1, 3000)
    power_rx_single = rec_power(distance, freq, h_tx, h_rx)
    power_rx_single_db = to_decibel(power_rx_single)
    min_power_single = min_rec_power_single_freq(d_min, d_max, freq, h_tx, h_rx)
    min_power_single_db = to_decibel(min_power_single)
    LOGGER.info(f"Minimum power single frequency: {min_power_single_db:.2f} dB")

    opt_df = find_optimal_delta_freq(d_min, d_max, freq, h_tx, h_rx, c)
    LOGGER.info(f"Optimal frequency spacing: {opt_df:E}")
    power_rx_opt = sum_power_envelope(distance, opt_df, freq, h_tx, h_rx)
    power_rx_opt_db = to_decibel(power_rx_opt)
    min_power_two = sum_power_envelope(d_max, opt_df, freq, h_tx, h_rx)
    min_power_two_db = to_decibel(min_power_two)
    LOGGER.info(f"Minimum power two frequencies: {min_power_two_db:.2f} dB")

    power_rx_opt_exact = .5*(power_rx_single + rec_power(distance, freq+opt_df, h_tx, h_rx))
    power_rx_opt_exact_db = to_decibel(power_rx_opt_exact)

    results = {"distance": distance, "powerSingle": power_rx_single_db,
               "powerOpt": power_rx_opt_db,
               "powerOptExact": power_rx_opt_exact_db}

    if plot:
        fig, axs = plt.subplots()
        axs.semilogx(distance, power_rx_single_db, '-b', label="Single Frequency")
        axs.semilogx(distance, power_rx_opt_db, '-r', label="Lower Bound")
        axs.semilogx(distance, power_rx_opt_exact_db, '--r', alpha=.5, label="Two Freq. - Optimal$\Delta f$")
        axs.set_xlabel("Distance $d$ [m]")
        axs.set_ylabel("Receive Power $P_r$ [dB]")
        axs.set_title(f"Parameters: $f_1=${freq:E} Hz,\n$h_{{tx}}={h_tx:.1f}$ m, $h_{{rx}}={h_rx:1f}$ m,\n$d_{{min}}={d_min:.1f}$ m, $d_{{max}}={d_max:.1f}$ m")
    if export:
        LOGGER.debug("Exporting results.")
        export_results(results, f"power_opt_freq-{freq:E}-t{h_tx:.1f}-r{h_rx:.1f}-dmin{d_min:.1f}-dmax{d_max:.1f}.dat")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.)
    parser.add_argument("-r", "--h_rx", type=float, default=1.)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-dmin", "--d_min", type=float, default=10.)
    parser.add_argument("-dmax", "--d_max", type=float, default=100.)
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
    main_optimal_frequency_distance(**args)
    plt.show()
