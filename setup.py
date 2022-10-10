from setuptools import setup

setup(
    name="clickuphelper",
    version="0.1.0",
    py_modules=["clickuphelper"],
    packages=["clickuphelper"],
    install_requires=["requests", "click"],
    entry_points={
        "console_scripts": [
            "clickuphelper=clickuphelper.cli:cli",
        ],
    },
)
