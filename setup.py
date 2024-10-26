from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clickuphelper",
    version="0.3.6",
    py_modules=["clickuphelper"],
    packages=["clickuphelper"],
    install_requires=["requests", "click"],
    entry_points={
        "console_scripts": [
            "clickuptask=clickuphelper.cli:task",
            "clickuptree=clickuphelper.cli:tree",
            "clickuplist=clickuphelper.cli:clickuplist",
            "clickuptime=clickuphelper.cli:clickuptime",
        ],
    },
    author="Richmond Newman",
    author_email="newmanrs@gmail.com",
    description="A CLI tool for interacting with ClickUp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/newmanrs/clickuphelper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
