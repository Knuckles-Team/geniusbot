#!C:\Users\knuck\Documents\Python\GeniusBot\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'astropy==4.0.1.post1','console_scripts','fitsinfo'
__requires__ = 'astropy==4.0.1.post1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('astropy==4.0.1.post1', 'console_scripts', 'fitsinfo')()
    )
