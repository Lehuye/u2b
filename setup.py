from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'includes': ['PyQt5'],
    'packages': [],
    'frameworks': [],  # 👈 避免直接包含 QtFramework
    'excludes': ['tkinter'],  # 可选
    'resources': ['icon.icns'],  # 若有图标
    'optimize': 1,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)