This script auto extracts the Voc of the given temperature and irradiance from [PVSyst](https://www.pvsyst.com/)

![screenshot](./res/img/auto_fill.gif?raw=true "Title")

## Installation
- download and install [python3.6.8](https://www.python.org/ftp/python/3.6.8/python-3.6.8.exe)
- open the ```cmd``` windows in the same project folder
- run ```pip install -r requirements.txt``` in ```cmd``` terminal to install needed python package
- modify temperature and irradiation values in config.txt file

## To run
- open PVSyst.exe
- open windows 'Definition of a PV module'
- make sure the windows is visible on Desktop (i.e. not hidden)
![screenshot](./res/img/screenshot.png?raw=true "Title")
- run ```python main.py``` in ```cmd``` terminal
- [demo video](https://youtu.be/hc7bJUA81ZI)

## Output
- all result will be stored in csv folder, file name will depend on the selected PV module
- resule will append to the same file if already exists


## Note
- the tool only support Windows as PVSyst only support Windows
- the tool only support ```1920x1080``` resolution and single screen
- the tool will first capture the screen and identify the key buttons location on the screen