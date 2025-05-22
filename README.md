# whisperXapp
A simple interactive UX interface for whisperX using widgets in jupyter notebooks.

<img src="screenshot_whisperxapp.png" alt="whisperXapp" style="display:block; margin: 0 auto;" width="50%"/>

## Installation
``` bash
python3.11 -m venv venv3.11_whisperxapp
source venv3.11_whisperxapp/bin/activate
git clone --recursive https://github.com/Global-Health-Engineering/whisperXapp.git
cd whisperXapp
pip install -e whisperx/.
pip install ipykernel ipywidgets
ipython kernel install --user --name=venv3.11_whisperxapp
```