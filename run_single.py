import os
import sys
from pprint import pprint
from glob import glob

sys.path.append(os.path.dirname(__file__) + '/src')

from nutrients_parser import parse_html

filename = sys.argv[1]
with open(filename, 'r') as f:
    pprint(parse_html(f.read(), language="NL"))
    pprint("end")
