######################################################################
#                                                                    #
#   This file ontains the code used to generate the pulse sequence   #
#   waveforms for the BME 599 Visualization Project (2025).          #
#                                                                    #
#   Written by                                                       #
#   - Andrea Jacobsen                                                #
#   - Christopher Louly                                              #
#                                                                    #
######################################################################

import numpy as np

pi = np.pi
gambar = 42570                  # Gyromagnetic coefficient [kHz/T]
gam = gambar * 2 * 3.14159      # Gamma [kRad/sT]


def fse_pulsetrain(T, PW, ETL, TE, dt):
    """
    This function generates a B1 pulsetrain for a spin echo with:

    T:      Simulation Time [ms]
    PW:     Excitation and Refocuser Pulse Width [ms]
    ETL:    Number of echos
    TE:     Echo Time [ms]
    dt:     Simulation Timestep [ms]

    Output:
    B:      A (ntime, 3) numpy array containing the X, Y, and Z components
            of the B1 pulsetrain at each sample time in the rotating frame.
    """
    # Number of timepoints
    ntime = np.int64(np.ceil(T / dt))

    # Initializing Final output
    B = np.zeros((ntime, 3))

    # Number of indices covered by one pulse and one echo respectively
    p_len = int(np.ceil(PW / dt))
    echo_len = int(np.ceil(TE / dt))

    # Pulse Area Scaling Constant
    scale = pi / (180 * gam * p_len * dt)

    # The first 90 degree pulse
    B[0:p_len, 0] = 90 * scale

    # Add the refocuser pulses
    cur_idx = int(echo_len / 2)

    for _ in range(ETL):
        B[cur_idx: cur_idx + p_len, 0] = 180 * scale
        cur_idx += echo_len

    return B


def fse_freq_enc_grad(G_amp, G_dur, T, PW, ETL, TE, dt):
    # Number of timepoints
    ntime = np.int64(np.ceil(T / dt))

    # Initializing Final output
    G = np.zeros((ntime,))

    # Number of indices covered by one gradient pulse and one echo respectively
    g_len = int(np.ceil(G_dur / dt))
    echo_len = int(np.ceil(TE / dt))

    # Add the Freq. Enc. Prewinder
    G[int((echo_len - g_len) / 4):int((echo_len + g_len) / 4)] = G_amp

    # Add the refocuser pulses
    cur_idx = echo_len - int(g_len / 2)

    for _ in range(ETL):
        G[cur_idx: cur_idx + g_len] = G_amp
        cur_idx += echo_len

    return G
