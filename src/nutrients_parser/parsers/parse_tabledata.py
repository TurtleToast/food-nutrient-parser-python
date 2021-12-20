from ..functions.identifiers import *
from pprint import pprint

"""
Getting
[
    ['energie', 'kJ 577 / kcal 137', 'kJ 2596 / kcal 617'],
    ['vetten', '4.4 g', '19.8 g'],
    ['waarvan verzadigde vetzuren', '0.8 g', '3.6 g'],
    ['koolhydraten', '17.4 g', '78.3 g'],
    ['waarvan suikers', '3.6 g', '16.2 g'],
    ['vezels', '1.6 g', '7.2 g'],
    ['eiwitten', '6.2 g', '27.9 g'],
    ['zout', '0.50 g', '2.25 g'],
    ['Deze verpakking bevat 1 portie.']
]
Wanting
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
    ],
    [
        ['koolhydraten'],
        ['17.4 g', '78.3 g']
    ],
    [
        ['waarvan suikers'], 
        ['3.6 g', '16.2 g']
    ],
    [
        ['vezels'],
        ['1.6 g', '7.2 g']],
    [
        ['eiwitten'],
        ['6.2 g', '27.9 g']
    ],
    [
        ['zout'],
        ['0.50 g', '2.25 g']
    ]
]
"""


def parse_tabledata(data, language="NL"):
    # NOTE Asumptions:
    # There is one nutrient per row
    # Values and units are in the same row as the nutrient
    # We look for the values and nutrients based on common pattern as we assume that they will be on the same place throughout the table

    # If there is nothing, there is no point.
    if len(data) == 0:
        return None

    # Create main object
    nutrientObject = []

    # Get the i's of the nutrient and of the values and units
    # NOTE the nutrient i is a single number where the of the values and units is an array
    nutrientI = checkForNutrientI(data, language=language)
    valueI = checkForValueAndUnitI(data, language=language)

    # If no nutrients and or values have been found, there is no point to continue :(
    if nutrientI == None or valueI == None:
        print("No nutrient or value i found.")
        return None

    # Main loopylooploop
    for row in data:
        if (len(row) < max(valueI) + 1):
            continue
        
        # Pre made array where 0: nutrient, 1: value(s)
        newRow = [[], []]

        # Extracting the I's and placing them into the premade array
        for i, thing in enumerate(row):
            if i == nutrientI:
                newRow[0].append(thing)
            if i in valueI:
                newRow[1].append(thing)

            if i + 1 == len(row):
                nutrientObject.append(newRow)

    return cleanData(nutrientObject)

def cleanData(data):
    filtert = []
    for x in data:
        if x[0][0] is not None:
            filtert.append(x)
    
    return filtert

def checkForNutrientI(data, language="NL"):
    # Make empty list
    iArray = []

    # Looping over data
    for nutrientArray in data:
        for i, word in enumerate(nutrientArray):
            # If we encounter a nutrient, lets save the i
            if(identifyNutrient(stringArray=word, language=language)):
                iArray.append(i)

    # Check if we have found any nutrients
    if len(iArray) > 0:
        # If so, we allow only 1 nutrient I meaning we get the most common i
        return max(set(iArray), key=iArray.count)

    # Else we return nothing found
    return None


def checkForValueAndUnitI(data, language="NL"):
    # Make empty list
    iArray = []

    # Looping over data
    for valueArray in data:
        for i, word in enumerate(valueArray):
            # If we encounter an unit or value, we save the i, only if we not saved the spot before.
            if identifyUnit(word, language=language) or identifyValue(word, exact=True):
                if i not in iArray:
                    iArray.append(i)

    # Check if we found any values and or units
    if len(iArray) > 0:
        iArray.sort()
        return iArray

    # else return nothing found
    return None