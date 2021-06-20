# Data Collection in the World Wide Web

## Installation

Please install Python >= 3.9 either via download from the official 
[Python website](https://www.python.org/downloads/) or using your preferred package manager.

```shell
# MacOS
brew install python@3.9

# Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.9
```

Install virtual environment package using pip. Please use `pip3` to ensure that it uses Python 3.x.

```shell
pip3 install --user virtualenv
```

Create a new virtual environment using the new available `venv` command. The virtual will be setup
in a folder called `venv`.

```shell
python3 -m venv venv
```

After installing, you have to activate the virtual environment using the `activate` script. Please
ensure to use the correct commanding for your operating system.

```shell
# MacOS or Linux
source env/bin/activate

# Windows
.\env\Scripts\activate
```

Install the project dependencies using the requirements file.

```shell
pip install -r requirements.txt
```

Deactivate the project environment. The environment is automatically closed if you close your 
terminal.

```shell
deactivate
```
