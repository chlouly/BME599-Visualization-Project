#########################################################################
#                                                                       #
#   This file ontains the code used to generate plots and aniimations   #
#   for the BME 599 Visualization Project (2025).                       #
#                                                                       #
#   Written by                                                          #
#   - Andrea Jacobsen                                                   #
#   - Christopher Louly                                                 #
#                                                                       #
#########################################################################

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

def plot_iso_3D(M, save_path=None, display=False, dsamp=1, yz_view=True):
    # Quick Check, if we do not need to display or save, nothing to be done.
    if (save_path == None) and (display == False):
        return

    # Get Data Dimensions
    if len(M.shape) == 3:
        ntime, _, num_iso = np.shape(M)
    elif len(M.shape) == 2:
        ntime, _ = np.shape(M)
        num_iso = 1
        M = np.reshape(M, (ntime, 3, num_iso))

    # Define a vector of color values for the arrows
    color_vec = np.linspace(0, 1, num_iso)

    # Set Up the figure
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim([-1,1]); ax.set_ylim([-1,1]); ax.set_zlim([-1,1])
    ax.set_box_aspect([1,1,1])
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])

    # If we want the view along the yz axis, do this
    if yz_view:
        ax.view_init(0, 90)

    # Set the 3D Axes
    ax.plot([-1, 1], [0, 0], [0, 0], color='black', linewidth=2)  # X-axis
    ax.plot([0, 0], [-1, 1], [0, 0], color='black', linewidth=2)  # Y-axis
    ax.plot([0, 0], [0, 0], [-1, 1], color='black', linewidth=2)  # Z-axis  
    ax.text(1.1, 0, 0, 'X', fontsize=14)
    ax.text(0, 1.1, 0, 'Y', fontsize=14)
    ax.text(0, 0, 1.1, 'Z', fontsize=14)

    # Create the Initial Quiver Object
    quiv = ax.quiver(
        np.zeros(num_iso), np.zeros(num_iso), np.zeros(num_iso),   # tails
        M[0,0,:], M[0,1,:], M[0,2,:],  # directions
        length=1, normalize=False, cmap='jet'
    )
    quiv.set_array(color_vec)

    # Create the Update Function for the Animation
    #   This must be a nested function definition because
    #   it's function signature must not include other imputs, but
    #   it must reference external variables found of the scope of 
    #   'plot_3d_mag()'
    def update(frame):
        nonlocal quiv
        quiv.remove()   # remove old arrows
        quiv = ax.quiver(
            np.zeros(num_iso), np.zeros(num_iso), np.zeros(num_iso),
            M[frame*dsamp,0,:], M[frame*dsamp,1,:], M[frame*dsamp,2,:],
            length=1, normalize=False, cmap='jet'
        )
        quiv.set_array(color_vec)
        return quiv,

    # Do the actual Animation
    anim = FuncAnimation(fig, update, frames=int(ntime / dsamp), interval=30, blit=False)

    # Save the animation to the path given (if any)
    if save_path != None:
        anim.save(save_path, fps=30, dpi=150)
        print(f"Animation saved to: {save_path}")

    # Show the animation (if desired)
    if display:
        plt.show()
