import os
import json
from ..functions.regex import *
import re as regex

# JSON Loading
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__+'/../lang', 'languages.json')) as json_data:
    languageJsonObject = json.load(json_data,)


def identifyNutrient(array=None, string=None, stringArray=None, language="NL"):
    if(array == None and string == None and stringArray == None):
        return None

    langObject = languageJsonObject[language]["nutrients"]

    if array:
        # Loop through the nutrient list
        for nutrient in langObject:
            # Force max length of word depth to be first considered
            for i in reversed(range(nutrient["maxWordLength"])):
                # Make sure that we don't go beyond the array index
                if len(array) - 1 >= i:
                    # Concat all the words from the array
                    regexCheckText = ' '.join(array[:i+1])
                    if regexMatch(nutrient["regex"], regexCheckText):
                        return {"nutrient": nutrient, "orginalText": regexCheckText}
    if string:
        # Loop through the nutrient list
        for nutrient in langObject:
            if regexMatch(nutrient["regex"], string):
                return {"nutrient": nutrient, "orginalText": string}

    if stringArray:
        array = stringArray.split()
        defaultUnit = None
        # Loop through the nutrient list
        for nutrient in langObject:
            # Force max length of word depth to be first considered
            for i in reversed(range(nutrient["maxWordLength"])):
                # Make sure that we don't go beyond the array index
                if len(array) - 1 >= i:
                    # Concat all the words from the array
                    regexCheckText = ' '.join(array[:i+1])
                    if regexMatch(nutrient["regex"], regexCheckText):
                        if len(array) >= i+2:
                            defaultUnit = identifyUnit(array[i+1])
                        return {"nutrient": nutrient, "orginalText": regexCheckText, "defaultUnit": defaultUnit}
    return None


def identifyValue(string, exact=False):
    if(string == None):
        return None

    # Ignore all %
    if regexSearch('%', string):
        return None

    # Get possible match filtering on numbers
    if exact:
        possibleMatch = regexMatch('[0-9]+(.[0-9])?', string)
    else:
        possibleMatch = regexSearch('[0-9]+(.[0-9])?', string)

    if possibleMatch:
        # Return first result
        return possibleMatch.group(0)
    return None


def identifyUnit(string, language="NL"):
    if(string == None):
        return None

    langObject = languageJsonObject[language]["units"]

    # Loop over all units
    for unit in langObject:
        # Sanitize the unit, strip it and exact match
        if regexMatch(unit["regex"], regexSub('\(|\)|:|\/|[0-9]+(.[0-9])?', '', string)):
            return unit
    return None


def identifyPer(string, language="NL"):
    if(string == None):
        return None

    return regexSearch(languageJsonObject[language]["per"], string)
