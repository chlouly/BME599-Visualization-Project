# BME 599 Visualization Project
##### Andrea Jacobson, Christopher Louly </br> Due Tue 12/09/2025



This repository contains all the code to perform Bloch Simulations and create plots for the Fall 2025 BME599 Visualization Project. All of the actual Bloch Simulation code can be found in `./UM_Blochsim/`, which was written in C for efficiency by the the authors of this submission before this project was assigned. This is an adaptation of the code found in https://github.com/chlouly/UM_Blochsim so that it may be used by anyone wishing to run this code without cloning and installing UM_Blochsim.



**USAGE:** 

For the animations to render and save, you must have `ffmpeg` installed on your machine, sorry for the inconvenience. Once ffmpeg is installed, you must update the `FFMPEG_PATH` variable in `main.ipynb` to reflect the path to `ffmpeg` on your machine. In bash (or most other shells), you can run `$ which ffmpeg` to retrieve the path.

Please run this code on a Unix based machine. The shared object file `UM_Blochsim.so` will not work on a windows machine. Before running the contents of this file, please run `$ make` inside of `./UM_Blochsim/` directory to recompile the shared object file using your local C compiler. This will ensure that the Blochsim code is compatible with you machine.



`Thank You :)`