import os
import sys
from pprint import pprint

sys.path.append(os.path.dirname(__file__) + '/src')

from nutrients_parser import parse_htmldata, parse_tabledata, parse_perdata, parse_valuedata, parse_combinedata

language = "NL"

filename = sys.argv[1]
with open(filename, 'r') as f:
    tabledata, perdata = parse_htmldata(f.read(), language=language)
    #pprint(tabledata)
    perdata = parse_perdata(perdata, language=language)
    #pprint(perdata)
    tabledata = parse_tabledata(tabledata, language=language)
    #pprint(tabledata)
    tabledata = parse_valuedata(tabledata, language=language)
    #pprint(tabledata)
    nutrientData = parse_combinedata(tabledata, perdata)
    pprint(nutrientData)
    
    pprint("end")