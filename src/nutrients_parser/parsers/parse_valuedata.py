from nutrients_parser.functions.regex import regexSub
from ..functions.identifiers import *
from pprint import pprint

"""
Getting
[
    [
        ['energie'],
        ['kJ 577 / kcal 137', 'kJ 2596 / kcal 617']
    ],
    [
        ['vetten'],
        ['4.4 g', '19.8 g']
    ],
    [
        ['waarvan verzadigde vetzuren'],
        ['0.8 g', '3.6 g']
    ]
]
Wanting
[
    [
        ['energie'],
        [
            [
                {'orginalText': 'kJ 577', 'unit': 'Kilojoules', 'value': '577'},
                {'orginalText': 'kcal 137', 'unit': 'Calories', 'value': '137'}
            ],
            [
                {'orginalText': 'kJ 2596', 'unit': 'Kilojoules', 'value': '2596'},
                {'orginalText': 'kcal 617', 'unit': 'Calories', 'value': '617'}
            ]
        ]
    ],
    [
        ['vetten'],
        [
            [
                {'orginalText': '4.4 g', 'unit': 'Gram', 'value': '4.4'}
            ],
            [
                {'orginalText': '19.8 g', 'unit': 'Gram', 'value': '19.8'}
            ]
        ]
    ],
    [
        ['waarvan verzadigde vetzuren'],
        [
            [
                {'orginalText': '0.8 g', 'unit': 'Gram', 'value': '0.8'}
            ],
            [
                {'orginalText': '3.6 g', 'unit': 'Gram', 'value': '3.6'}
            ]
        ]
    ]
]
"""


def parse_valuedata(data, language="NL"):
    # NOTE Assuming the following:
    # That a default unit will always be at the end of a nutrient.

    # If there is nothing, there is no point.
    if len(data) == 0:
        return None

    # Main loopylooploop
    for i, row in enumerate(data):
        # Keep in mind that [i][0] = nutrientArray[0] = nutrient and [i][1] = values
        data[i][0][0], defaultUnit = checkForDefaultUnit(data[i][0][0], language=language);
        data[i][1] = extractValuesAndUnits(data[i][1], defaultUnit, language=language)

    return data

def checkForDefaultUnit(nutrientString, language="NL"):
    # Split the complete nutrient string, if a default 
    stringArray = nutrientString.split()

    if len(stringArray) > 1:
        defaultUnit = identifyUnit(stringArray[len(stringArray) - 1], language=language)
        
        if defaultUnit:
            return stringArray[:-1], defaultUnit

    return nutrientString, None

def extractValuesAndUnits(valueArray, defaultUnit, language="NL"):
    for i, x in enumerate(valueArray):
        valueArray[i] = extractValuesAndUnitsFromWords(x, defaultUnit, language=language)

    return valueArray

def extractValuesAndUnitsFromWords(string, defaultUnit, language="NL"):
    # Make default array
    arrayToReturn = []

    # Set default vars
    currentValue = None
    currentUnit = None
    maxDepthToGo = 2
    currentDepth = maxDepthToGo
    orginalText = ""
    firedOnce = False

    loopArray = string.split()

    # Loop through the entire array, we need to keep track of what we used and not used
    for i, word in enumerate(loopArray):
        # Keep track of the depth
        currentDepth -= 1

        # Check for a possible value but only if the value is not set
        if currentValue == None:
            possibleValue = identifyValue(word)
            if possibleValue:
                orginalText = orginalText + " " + word
                # Set data
                currentValue = possibleValue
                currentDepth = maxDepthToGo
                # Remove value bit from the word as the unit could be glued to the value
                word = regexSub('[0-9]+(.[0-9])?', '', word)

        # Check for a possible unit but only if the unit is not set
        if currentUnit == None:
            possibleUnit = identifyUnit(word, language=language)
            if possibleUnit:
                orginalText = orginalText + " " + word
                # Set data
                currentUnit = possibleUnit
                currentDepth = maxDepthToGo

        # Check if both Value and Unit are set meaning a single nutrient row is complete
        if currentValue != None and currentUnit != None:
            # Yup
            firedOnce = True

            # Add the data
            arrayToReturn.append({"value": currentValue, "unit": currentUnit["name"], "orginalText": orginalText.strip()})
            
            # Reset data to be able to take multiple values per nutrient for multiple per data
            currentValue = None
            currentUnit = None
            orginalText = ""
            currentDepth = maxDepthToGo

        # If max depth is reased (so if the current depth is 0)
        if currentDepth == 0 or i + 1 == len(loopArray):
            if currentValue != None or currentUnit != None or firedOnce == False:
                # If the unit is none, last hope is the default unit
                if currentUnit == None:
                    currentUnit = defaultUnit

                # Unit is an object containing a lot of data, for now we only use the name
                if currentUnit:
                    currentUnit = currentUnit["name"]
                # Add the data
                arrayToReturn.append({"value": currentValue, "unit": currentUnit, "orginalText": orginalText.strip()})
            
            # Break as max depth reased
            break

    return arrayToReturn