import UM_Blochsim as bs
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm

mpl.rcParams['animation.ffmpeg_path'] = "/usr/bin/ffmpeg"

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
    TE = 80     # 20ms TE
    ETL = 8    # 20 echos
    PW = 2   
    time_pad = 5   

    # Simulation Parameters
    T = ETL * TE + (TE / 2)     # Total Simulation Durration in ms
    dt = 0.01                    # Timestep in ms
    ntime = int(np.ceil(T / dt))

    # Tissue Parameters
    T1 = 800
    T2 = 30

    # Create B1
    B, T = fse_pulsetrain(PW, ETL, TE, dt, start_pad=time_pad)

    ntime = B.shape[0]

    # Make time vector for plotting
    time = np.arange(ntime) * dt

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

    # # Simulate
    # plotM=True
    # M = bs.blochsim_eul(B, T1, T2, dt, plot=plotM)

    # # Display Signal
    # S = np.linalg.norm(M[:, 0:2], axis=1)

    # # Plot Signal
    # T2_sig = np.exp(-time / T2)

    # plotS=False
    # if plotS:
    #     plt.plot(time, S, l'/opt/homebrew/bin/ffmpeg'abel="Observed Signal")
    #     plt.plot(time, T2_sig, label="T2 Decay Curve")
    #     plt.xlabel("Time [ms]")
    #     plt.ylabel("Signal")
    #     plt.legend()
    #     plt.show()





    ## --- MULTI ISOCHROMAT --- ##
    vox_x = 10**-3
    vox_y = 10**-3
    vox_z = 10**-3
    G_dur = 30
    G_amp = 0.005

    num_iso = 50
    iso_pos = np.zeros((num_iso, 3))
    iso_pos[:, 0] = np.linspace(-vox_z / 2, vox_z / 2, num_iso)

    # Make Gradient
    # TODO: Make Gradient Waveform
    # G_fe = fse_freq_enc_grad(G_amp, G_dur, T, PW, ETL, TE, dt)
    # G = np.zeros((G_fe.shape[0], 3))
    # G[:, 2] = G_fe
    # G = initial_pad(G, time_pad, dt)
    G, T_G = fse_freq_enc_grad(G_amp, G_dur, ETL, TE, dt, start_pad=time_pad, dim=0)

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
        print(B_eff.shape)
        M_all[:, :, n] = bs.blochsim_rk4(B_eff, T1, T2, dt)

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
        plt.title(f"FSE Signal Strength (T2 = {T2}ms)")
        plt.show()


    dsamp = 50

    # Colors
    color_vec = np.linspace(0, 1, num_iso)

    # ---- Set up figure ----
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim([-1,1]); ax.set_ylim([-1,1]); ax.set_zlim([-1,1])
    ax.set_box_aspect([1,1,1])
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])

    ax.plot([-1, 1], [0, 0], [0, 0], color='black', linewidth=2)  # X-axis
    ax.plot([0, 0], [-1, 1], [0, 0], color='black', linewidth=2)  # Y-axis
    ax.plot([0, 0], [0, 0], [-1, 1], color='black', linewidth=2)  # Z-axis  

    ax.text(1.1, 0, 0, 'X', fontsize=14)
    ax.text(0, 1.1, 0, 'Y', fontsize=14)
    ax.text(0, 0, 1.1, 'Z', fontsize=14)

    # Quiver object
    quiv = ax.quiver(
        np.zeros(num_iso), np.zeros(num_iso), np.zeros(num_iso),   # tails
        M_all[0,0,:], M_all[0,1,:], M_all[0,2,:],  # directions
        length=1, normalize=False, cmap='jet'
    )
    quiv.set_array(color_vec)

    # ---- Animation function ----
    def update(frame):
        nonlocal quiv
        quiv.remove()   # remove old arrows
        quiv = ax.quiver(
            np.zeros(num_iso), np.zeros(num_iso), np.zeros(num_iso),
            M_all[frame*dsamp,0,:], M_all[frame*dsamp,1,:], M_all[frame*dsamp,2,:],
            length=1, normalize=False, cmap='jet'
        )
        quiv.set_array(color_vec)
        return quiv,

    anim = FuncAnimation(fig, update, frames=int(ntime / dsamp), interval=30, blit=False)

    anim.save("SE.mp4", fps=30, dpi=150)
    plt.show()
    



if __name__ == "__main__":
    main()
