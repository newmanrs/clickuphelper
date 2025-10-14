# Stephen's notes

- Make sure to use the virtual environment to do this work.
- Pypi username: stevejb


``` shell
.venv/bin/python -m build
.venv/bin/python setup.py sdist bdist_wheel
twine upload dist/*
```
  
