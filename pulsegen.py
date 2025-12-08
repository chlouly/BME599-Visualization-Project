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


def fse_pulsetrain(PW, ETL, TE, dt, start_pad=0):
    """
    This function generates a B1 pulsetrain for a spin echo with:

    PW:     Excitation and Refocuser Pulse Width [ms]
    ETL:    Number of echos
    TE:     Echo Time [ms]
    dt:     Simulation Timestep [ms]

    Outputs:
    B:      A (ntime, 3) numpy array containing the X, Y, and Z components
            of the B1 pulsetrain at each sample time in the rotating frame
    T:      Total RF Waveform durration [ms]
    """

    # Input Validation:
    if dt <= 0:
        raise ValueError("Error, timestep (dt) must be positive")
    if start_pad < 0:
        raise ValueError("Error, initial dead time (start_pad) must be non-negative")
    

    # Number of indices covered by one pulse and one echo respectively
    p_len = int(np.ceil(PW / dt))
    echo_len = int(np.ceil(TE / dt))

    # Initialize Output Vector
    #   (Only the first pulse for now, the refocusers get appended later)
    B = np.zeros((int(echo_len / 2), 3))

    # Pulse Area Scaling Constant
    scale = pi / (180 * gam * p_len * dt)

    # The first 90 degree pulse
    B[0:p_len, 0] = 90 * scale

    # Add the refocuser pulses
    refoc_block = np.zeros((echo_len, 3))           # Initialize one refocuser pulse block
    refoc_block[0:p_len, 0] = 180 * scale           # Create the refocuser pulse in the block
    all_refoc = np.tile(refoc_block, (ETL, 1))      # Repeate refocuser pulses ETL times
    assert(all_refoc.shape[1] == 3)                 # Make sure the replication worked propperly
    B = np.append(B, all_refoc, axis=0)             # Combine with the excitation pulse to get the full B1 waveform

    # If we desire an initial dead time, add it now
    if start_pad > 0:
        B = initial_pad(B, start_pad, dt)

    # Calculate total RF Waveform Durration
    T = dt * B.shape[0]     # [ms]

    return B, T



def fse_freq_enc_grad(G_amp, G_dur, ETL, TE, dt, start_pad=0, dim=0):
    """
    This function generates a B1 pulsetrain for a spin echo with:

    G_amp:  Gradient Pulse Amplitude [T/cm]
    G_dur:  Gradient Pulse Durration [ms]
    ETL:    Number of echos
    TE:     Echo Time [ms]
    dt:     Simulation Timestep [ms]

    Outputs:
    G:      A (ntime, 3) numpy array containing the X, Y, and Z Gradient waveforms [T/cm]
    T:      Total RF Waveform durration [ms]
    """

    # Input Validation:
    if dt <= 0:
        raise ValueError("Error, timestep (dt) must be positive")
    if start_pad < 0:
        raise ValueError("Error, initial dead time (start_pad) must be non-negative")
    if dim < 0 or dim > 2:
        raise ValueError("Error, the dimension for frequency encoding must be 0, 1, or 2")
    

    # Number of indices covered by one gradient pulse and one echo respectively
    g_len = int(np.ceil(G_dur / dt))
    echo_len = int(np.ceil(TE / dt))

    # Initialize Output Vector
    #   (Only the first pulse for now, the refocusers get appended later)
    G = np.zeros((int(echo_len / 2), 3))

    # Add the Freq. Enc. Prewinder
    G[int((echo_len - g_len) / 4):int((echo_len + g_len) / 4), dim] = G_amp

    # Add the frequency encoding gradients
    fenc_block = np.zeros((echo_len, 3))            # Initialize one frequency encoding gradient block
    fenc_block[
        int((echo_len - g_len) / 2):
        int((echo_len + g_len) / 2), dim] = G_amp   # Create the gradient in the block
    
    all_fenc = np.tile(fenc_block, (ETL, 1))        # Repeate blocks ETL times
    assert(all_fenc.shape[1] == 3)                  # Make sure the replication worked propperly
    G = np.append(G, all_fenc, axis=0)              # Combine with the prewinder to get the full gradient

    # If we desire an initial dead time, add it now
    if start_pad > 0:
        G = initial_pad(G, start_pad, dt)

    # Calculate total RF Waveform Durration
    T = dt * G.shape[0]     # [ms]

    return G, T



def initial_pad(V, pad_time, dt):
    """
    Pad the vector V with zeros in the beginning.

    Inputs:
    V:          The vector to be padded (along the 0th axis)
    pad_time:   The ammount of time to add to the beginning of V
    dt:         The timestep of V (Increment of time from index to index along axis 0) [ms]
    """

    num_zeros = int(np.ceil(pad_time / dt))
    vec_sh = V.shape[1:]
    pad_vec = np.zeros((num_zeros,) + vec_sh)

    return np.append(pad_vec, V, axis=0)
