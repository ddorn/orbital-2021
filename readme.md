# Violet

The prototype of this game was made in one weekend for the sub-Orbital game jam,
it was not submited in due time, as I was busy playing it... 


### Controls

You use the arrow keys to move around, and the space bar to do
anything else. Also pressing `P` toggles the pause/settings screen
and `R` restarts the game.


### Assets

Thanks to all the people who made assests I've used in this game ! 
All the graphics are mine, but I made none of the music and sound effects.

Music: [Power Bots Loop](https://www.dl-sounds.com/royalty-free/power-bots-loop/)

Effects:
 - https://www.freesoundslibrary.com/
 - https://mixkit.co/free-sound-effects/
 
 
### Building executables

This section is mostly for me, for future reference, but may be of use
to you if you are looking for examples of how to build pygame apps executables
with pyinstaller.

Currently, all build commands are in the [Makefile](./Makefile) and should create
three builds inside the `dist/` folder: 

 - the source zip
 - a windows executable
 - a linux executable
 
...Provided that the script is run in the right environment.
Thus the steps here are for the setup of the environment.

Once the environment is setup, `make` should be the only thing that is needed
to build or rebuild the binaries. Optionally `make zip`, `make linux` or `make windows`
will produce only the corresponding build.

#### For linux

You need python 3.8 installed. The rest is taken care of by poetry, 
but you could also install the dependencies yourself, setup a virtual environment 
(or not) and run the pyinstaller command.

Thus, the only missing dependency is
[poetry](https://python-poetry.org), that you can get
from the instructions on their website.
otherwise, install them with pip:

```shell script
python3.8 -m pip install .
```

#### For windows

I build the windows executable on my linux machine, with the help of wine.
Here are the steps:
 - Install wine from your packet manager
 - Download a [python 3.8 installer](https://www.python.org/downloads/windows/).
 - Install it in wine `wine path/to/python-3.8.8.exe`
    You may find that only the 32 bit version works, but it doesn't matter (I think),
    just pick one that works
 - Install the dependencies: `wine python.exe -m pip install pygame pyinstaller`
 - You should be fine running `./build.sh` now !