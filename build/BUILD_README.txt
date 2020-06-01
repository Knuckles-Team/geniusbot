# Build from build folder Windows: 
..\venv\Scripts\python .\setup.py build

# Build from build folder Linux: 
python3 ./setup.py build

# Build Dist from folder:
..\venv\Scripts\python .\setup.py bdist --format=msi

# Build dist from build folder Linux: 
python3 ./setup.py bdist --format=msi

# Build from root dir
.\venv\Scripts\python setup.py build

.\venv\Scripts\python setup.py bdist --format=msi
https://docs.python.org/3/distutils/builtdist.html
