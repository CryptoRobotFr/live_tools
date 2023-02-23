# live_tools

## Dev mode

After installing pyenv, pyenv-virtualenv, install any 3.10.x python version (example with 3.10.6) :

```sh
pyenv install 3.10.6
# You install a python virtual environement for your project
pyenv virtualenv 3.10.6 live_tools
```

Go to you project home directory and exec :

```sh
pyenv local live_tools
pyenv activate live_tools
```

Then install the python dependencies :

```sh
pip install -r requirements.txt
```

## Live mode

Project set-up:  

```sh
git clone https://github.com/CryptoRobotFr/live_tools.git  
bash ./live_tools/install.sh
```
