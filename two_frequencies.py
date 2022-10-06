import logging

import numpy as np
from scipy import constants
from scipy import optimize
import matplotlib.pyplot as plt

from util import export_results, to_decibel

from model import length_los, length_ref
from single_frequency import rec_power, crit_dist


LOGGER = logging.getLogger(__name__)

@np.vectorize
def bound_rec_power_two_freq(d_min: float, d_max: float,
                             delta_freq: float, freq: float,
                             h_tx: float, h_rx: float, theta: float = 0.5,
                             c=constants.c,
                             bound="lower"):
    _comb_func = np.min if bound == "lower" else np.max
    _dk_worst_func = np.max if bound == "lower" else np.min
    #delta_freq = np.abs(freq2 - freq)
    _crit_dist = crit_dist(delta_freq, h_tx, h_rx)
    idx_dk_range = np.where(np.logical_and(_crit_dist>=d_min, _crit_dist<=d_max))
    crit_dist_range = _crit_dist[idx_dk_range]
    if len(crit_dist_range) > 0:
        dk_worst = _dk_worst_func(crit_dist_range)
        _pow_dk = sum_power_envelope(dk_worst, delta_freq, freq, h_tx, h_rx,
                                     bound=bound, theta=theta)
    else:
        _pow_dk = np.inf if bound == "lower" else np.NINF
    _pow_dmin = sum_power_envelope(d_min, delta_freq, freq, h_tx, h_rx,
                                   bound=bound, theta=theta)
    _pow_dmax = sum_power_envelope(d_max, delta_freq, freq, h_tx, h_rx,
                                   bound=bound, theta=theta)
    return _comb_func([_pow_dmin, _pow_dk, _pow_dmax])

def sum_power_envelope(distance, delta_freq, freq, h_tx, h_rx, bound="lower",
                       theta=0.5, G_los=1, G_ref=1, c=constants.c, power_tx=1):
    d_los = length_los(distance, h_tx, h_rx)
    d_ref = length_ref(distance, h_tx, h_rx)
    freq2 = freq+delta_freq
    omega = 2*np.pi*freq
    omega2 = 2*np.pi*freq2
    delta_omega = omega2-omega
    _factor = power_tx*(c/2)**2
    A = theta/omega**2
    B = (1-theta)/omega2**2
    _part1 = A + B
    _part2 = 1/d_los**2 + 1/d_ref**2
    #_part1 = c**2/(4*d_los**2) * (1./omega**2 + 1./omega2**2)
    #_part2 = c**2/(4*d_ref**2) * (1./omega**2 + 1./omega2**2)
    #A = (c/(2*omega))**2
    #B = (c/(2*omega2))**2
    _part3 = 2/(d_los*d_ref) * np.sqrt(A**2 + B**2 + 2*A*B*np.cos(delta_omega/c*(d_ref-d_los)))
    if bound == "lower":
        _part3 = -_part3
    power_rx = _factor * (_part1 * _part2 + _part3)
    return power_rx

def sum_power(distance, delta_freq, freq, h_tx, h_rx, G_los=1, G_ref=1,
              c=constants.c, power_tx=1):
    pow_f1 = rec_power(distance, freq, h_tx, h_rx, G_los=G_los, G_ref=G_ref,
                       c=c, power_tx=power_tx)
    pow_f2 = rec_power(distance, freq+delta_freq, h_tx, h_rx, G_los=G_los,
                       G_ref=G_ref, c=c, power_tx=power_tx)
    return 0.5*(pow_f1+pow_f2)

def power_eve(distance, delta_freq, freq, h_tx, h_rx, theta=.5, G_los=1, G_ref=1,
              c=constants.c, power_tx=1):
    d_los = length_los(distance, h_tx, h_rx)
    d_ref = length_ref(distance, h_tx, h_rx)
    freq2 = freq+delta_freq
    omega = 2*np.pi*freq
    omega2 = 2*np.pi*freq2
    delta_omega = omega2-omega
    _part1 = (c/2)**2
    _part2 = theta/omega**2 + (1-theta)/omega2**2
    _part3 = (1/d_los + 1/d_ref)**2
    power_rx = power_tx * (_part1 * _part2 * _part3)
    return power_rx

def delta_freq_peak_approximation(distance, h_tx, h_rx, c=constants.c):
    d_los = length_los(distance, h_tx, h_rx)
    d_ref = length_ref(distance, h_tx, h_rx)
    a = (d_ref-d_los)/c
    return np.array([1, 2])/(2*a)




def main(delta_freq: float, freq: float, h_tx: float, h_rx: float,
         c=constants.c, plot=False, export=False):

    distance = np.logspace(0, 3, 2000)

    power_bob = sum_power(distance, delta_freq, freq, h_tx, h_rx)
    power_bob_db = to_decibel(power_bob)

    power_bob_lower = sum_power_envelope(distance, delta_freq, freq, h_tx, h_rx, bound="lower")
    power_bob_upper = sum_power_envelope(distance, delta_freq, freq, h_tx, h_rx, bound="upper")
    power_bob_l_db = to_decibel(power_bob_lower)
    power_bob_u_db = to_decibel(power_bob_upper)

    power_eve_bound = power_eve(distance, delta_freq, freq, h_tx, h_rx)
    power_eve_db = to_decibel(power_eve_bound)

    results = {"distance": distance,
               "bob": power_bob_db,
               "eve": power_eve_db,
               "lower": power_bob_l_db,
              }

    if plot:
        fig, axs = plt.subplots()
        axs.semilogx(distance, power_bob_db, label="Receive Power")
        axs.semilogx(distance, power_bob_l_db, label="Lower Bound")
        axs.semilogx(distance, power_bob_u_db, label="Upper Bound")
        axs.semilogx(distance, power_eve_db, label="Worst-Case Eve")
        axs.set_xlabel("Distance $d$ [m]")
        axs.set_ylabel("Receive Power ${P_s}$ [dB]")
        axs.legend()

    if export:
        LOGGER.debug("Exporting single frequency power results.")
        fname = f"power-{freq:E}-df{delta_freq:E}-t{h_tx:.1f}-r{h_rx:.1f}.dat"
        export_results(results, fname)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.)
    parser.add_argument("-r", "--h_rx", type=float, default=1.5)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-df", "--delta_freq", type=float, default=100e6)
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
