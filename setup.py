import sys
from distutils.core import setup

if __name__ == '__main__':
    major,minor,_,_,_ = sys.version_info
    if major != 3:
        print('Failed to install: Python 3 required')
        exit()

    setup(name='CalCardiac',
          version='1.0',
          py_modules=['dataEngineering/adiConversion/processing_components'])
