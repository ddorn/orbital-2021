



### Assets

Music: [Power Bots Loop](https://www.dl-sounds.com/royalty-free/power-bots-loop/)

Effects:
 - https://www.freesoundslibrary.com/
 - https://mixkit.co/free-sound-effects/
 
 
### Building executables

This section is mostly for me, for future reference, but may be of use
to you if you are looking for examples of how to build pygame apps executables.

Currently, all build commands are in [build.sh](./build.sh), and should create
the three builds inside the `build/` folder, provided that the script 
is run in the right environment. Thus the steps here are for the setup of the environment.

Once the environment is setup, `./build.sh` should be the only thing that is needed
to build or rebuild hte binaries.

#### For linux

You need python 3.8 installed. The rest is take care of by poetry, 
but you could also install the dependencies yourself, setup a virtual environment 
(or not) and run the pyinstaller command.

Thus, the only missing dependencies is
[poetry](https://python-poetry.org), that you can get
from the instructions on their website.
otherwise, install them with pip

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