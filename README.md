# whisperUX

``` bash
python3.11 -m venv venv3.11_whisperxapp
source venv3.11_whisperxapp/bin/activate
git clone --recursive ...
cd whisperxapp
pip install -e whisperx/.
pip install ipykernel ipywidgets
ipython kernel install --user --name=venv3.11_whisperxapp
```