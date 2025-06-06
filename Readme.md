# Description

This is a simple Python script for downloading YouTube videos.

# How to run
1, create venv
```bash
python3 -m venv venv
```

2, activate venv
```bash
source venv/bin/activate
```

use fish shell
```bash
source venv/bin/activate.fish
```

3, install requirements
```bash
python3 -m pip install -r requirements.txt
```

4, run
```bash
python3 main.py
```
# Development

1, building requirements.txt
```bash
python3 -m pip freeze > requirements.txt
```

2, Generate app for mac
```bash
python3 setup.py py2app
```