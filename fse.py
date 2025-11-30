import UM_Blochsim as bs
import numpy as np
import matplotlib.pyplot as plt

from pulsegen import *


# NOTES:
# This is just in case you wanna play with the parameters:
# - If the plots show |M(t)| > 1 that means dt is too large so make it smaller.
#   This could also happen if you make the gradient amplitudes too large.
# - if it tkaes forever to run, make dt bigger or make num_iso smaller at the cost of accuracy
# - I still have not found a good gradient amplitude to get the effect I expect to see with many isochromats



def main():
    ## --- SINGLE ISOCHROMAT --- ##
    # Sequence Parameters
    TE = 20     # 20ms TE
    ETL = 20    # 20 echos
    PW = 2      

    # Simulation Parameters
    T = ETL * TE + (TE / 2)     # Total Simulation Durration in ms
    dt = 0.1                    # Timestep in ms
    ntime = int(np.ceil(T / dt))

    # Tissue Parameters
    T1 = 1000
    T2 = 400

    # Make time vector for plotting
    time = np.arange(ntime) * dt

    # Create B1
    B = fse_pulsetrain(T, PW, ETL, TE, dt)

    # Plot B1 (for sanity)
    plotB=True
    if plotB:
        plt.plot(time, B[:, 0], label="Bx")
        plt.plot(time, B[:, 1], label="By")
        plt.plot(time, B[:, 2], label="Bz")
        plt.xlabel("Time [ms]")
        plt.ylabel("Magnetic Field Strength [T]")
        plt.legend()
        plt.show()

    # Simulate
    plotM=False
    M = bs.blochsim_eul(B, T1, T2, dt, plot=plotM)

    # Display Signal
    S = np.linalg.norm(M[:, 0:2], axis=1)

    # Plot Signal
    T2_sig = np.exp(-time / T2)

    plotS=False
    if plotS:
        plt.plot(time, S, label="Observed Signal")
        plt.plot(time, T2_sig, label="T2 Decay Curve")
        plt.xlabel("Time [ms]")
        plt.ylabel("Signal")
        plt.legend()
        plt.show()





    ## --- MULTI ISOCHROMAT --- ##
    vox_x = 10**-3
    vox_y = 10**-3
    vox_z = 10**-3
    G_dur = 10
    G_amp = 0.01

    num_iso = 50
    iso_pos = np.zeros((num_iso, 3))
    iso_pos[:, 2] = np.linspace(-vox_z / 2, vox_z / 2, num_iso)

    # Make Gradient
    # TODO: Make Gradient Waveform
    G = np.zeros((ntime, 3))
    G[:, 2] = fse_freq_enc_grad(G_amp, G_dur, T, PW, ETL, TE, dt)

    # Plot G (for sanity)
    plotG=True
    if plotG:
        plt.plot(time, G[:, 0], label="Gx")
        plt.plot(time, G[:, 1], label="Gy")
        plt.plot(time, G[:, 2], label="Gz")
        plt.xlabel("Time [ms]")
        plt.ylabel("Gradient Strength]")
        plt.legend()
        plt.show()

    # Simulate
    M_all = np.zeros((ntime, 3, num_iso))
    for n in range(num_iso):
        B_eff = B
        B_eff[:, 2] += np.sum(G * iso_pos[n, :], axis=1)
        M_all[:, :, n] = bs.blochsim_eul(B_eff, T1, T2, dt)

    # Average over all isochromats:
    M_total = np.mean(M_all, axis=2)

    # Signal
    S_total = np.linalg.norm(M_total[:, 0:2], axis=1)

    print(M_total.shape)
    print(M_all.shape)
    print((G * iso_pos[4, :]).shape)
    print(M_total)

    # Plot Signal
    plotS_tot=True
    if plotS_tot:
        plt.plot(time, S_total, label="Observed Signal")
        plt.xlabel("Time [ms]")
        plt.ylabel("Signal")
        plt.legend()
        plt.show()
    



if __name__ == "__main__":
    main()
