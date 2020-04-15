#!C:\Users\knuck\Documents\Python\GeniusBot\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'cx-Freeze==6.1','console_scripts','cxfreeze-quickstart'
__requires__ = 'cx-Freeze==6.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('cx-Freeze==6.1', 'console_scripts', 'cxfreeze-quickstart')()
    )
