from nutrients_parser.functions.regex import regexSub
from ..functions.identifiers import *
from pprint import pprint

"""
Getting
[
    ['\xa0'],
    ['per 100 g:'],
    ['Per 450 g:']
]
Wanting
[
    {'per':
        {
            'name': '100 Gram',
            'orginalText': 'per 100 g:',
            'unit': 'g',
            'value': '100'
        },
        'prepared': False,
        'rows': []
    },
    {'per':
        {
            'name': '450 Gram',
            'orginalText': 'Per 450 g:',
            'unit': 'g',
            'value': '450'
        },
        'prepared': False,
        'rows': []
    }
]
"""


def parse_perdata(data, language="NL"):
    # If there is nothing, there is no point.
    if len(data) == 0 or len(data[0]) == 0:
        return None

    # Create main object
    nutrientObject = []

    # Main loopylooploop
    for row in data:
        possiblePer = checkForPerData(row[0], language=language)
        if possiblePer:
            nutrientObject.append(possiblePer)

    return nutrientObject

def checkForPerData(string, language="NL"):
    array = string.split()
    # Identify if per trigger
    for i, word in enumerate(array):
        if identifyPer(word, language):
            # Return new per data
            return makePerData(array[i:])
    
    return None

def makePerData(array):
    if array == None or len(array) == 0:
        return None
    
    # Make new object, Name must be text because data is appended to it
    data = {"per": {"name": "", "value": None, "unit": None, "orginalText": None}, "prepared": False, "rows": []}

    # Set vars
    orginalText = ""

    # Loop over all words
    for i, word in enumerate(array):
        orginalText += " " + word

        # Check if Value and if no value is set yet
        possibleValue = identifyValue(word)
        if possibleValue and data['per']['value'] == None:
            # Set data
            data['per']['value'] = possibleValue
            data['per']['name'] = possibleValue + data['per']['name']
            # Remove bit from word is the unit is glued to the value
            word = regexSub('^[0-9]+(.[0-9])?', '', word)

        # Check if Unit and if no unit is set yet
        possibleUnit = identifyUnit(word)
        if possibleUnit and data['per']['unit'] == None:
            # Set data
            data['per']['unit'] = possibleUnit['notation']
            data['per']['name'] = data['per']['name'] + " " + possibleUnit['name']

        # Check if all data is set meaning it can end
        if data['per']['value'] != None and data['per']['unit'] != None:
            # Set data
            data['per']['orginalText'] = orginalText.strip()
            # Fix data if needed
            if data['per']['name'] == "":
                data['per']['name'] = None
            break

        if len(array) == i + 1:
            # Set data
            data['per']['orginalText'] = orginalText.strip()
            # Fix data if needed
            if data['per']['name'] == "":
                data['per']['name'] = None
            break
    return data


