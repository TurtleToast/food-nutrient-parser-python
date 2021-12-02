import enum
from nutrients_parser.functions.identifiers import identifyUnit, identifyValue, identifyNutrient
from nutrients_parser.functions.regex import regexSub
from ..lang import *
from ..functions.identifiers import *
from pprint import pprint

# Sweet looking end result :D
"""
{
    data: [
        {
            per: {
                name: "100 Gram",
                value: 100,
                unit: "g",
                orginalText: "100 Gram"
            },
            prepared: False,
            rows: [
                {name: "Energie",  code: "ENER-",  amount: {value: 1141,   unit: "kJ",   orginalText: "1141 kJ"}},
                {name: "Energie",  code: "ENER-",  amount: {value:  273,   unit: "kcal", orginalText: "273 kcal"}},
                {name: "Eiwitten", code: "CHOAVL", amount: {value:    7,   unit: "g",    orginalText: "7 g"}},
                {name: "Zout",     code: "SALTEQ", amount: {value:  0.9,   unit: "g",    orginalText: "0.9 g"}},
            ]
        }
    ]
}
"""


def parse_tabledata(data, language="NL"):
    # NOTE Asumptions:
    # There is one nutrient per row
    # Values and units are in the same row as the nutrient
    # Everything we want to have, we have defined in the languages.json

    # If there is nothing, there is no point.
    if len(data) == 0 or len(data[0]) == 0:
        return None

    pprint(data)

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
        possibleData = extractDataFromRow(
            row, nutrientI, valueI, language=language)
        if possibleData:
            nutrientObject = addRowDataToNutrientObject(
                possibleData, valueI, nutrientObject)

    return nutrientObject


def addRowDataToNutrientObject(data, valueI, object):
    if(len(object) == 0):
        object = [{"per": {"name": "", "value": None, "unit": None, "orginalText": None},
                   "prepared": False, "rows": []} for _ in range(len(valueI))]

    for i, row in enumerate(data):
        object[i]["rows"].extend(row)

    return object


def extractDataFromRow(row, nutrientI, valueI, language="NL"):
    # Proces has two stages, check for nutrient, check of values and units
    nutrient = extractNutrient(row, nutrientI, language=language)
    if(nutrient):
        return extractValuesAndUnits(nutrient, row, valueI, language=language)
    else:
        return None


def extractNutrient(data, i, language="NL"):
    # Simpel identify will do the trick
    pprint(identifyNutrient(stringArray=data[i], language=language))
    return identifyNutrient(stringArray=data[i], language=language)


def extractValuesAndUnits(nutrient, data, iArray, language="NL"):
    # We want to use the table structure so we need to create that structure! This based on the iArray, so no index errors possible
    arrayToReturn = [[] for _ in range(len(iArray))]

    # Loop over the iArray to be able to look at the possible data we need
    for y, i in enumerate(iArray):
        arrayToReturn[y].extend(extractValuesAndUnitsFromWords(
            data[i], nutrient, language=language))

    # Return if anything
    if len(arrayToReturn) > 0:
        return arrayToReturn

    # Else return nothing
    return None


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


def extractValuesAndUnitsFromWords(string, nutrient, language="NL"):
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
            arrayToReturn.append({"name": nutrient["nutrient"]["name"], "code": None, "amount": {
                "value": currentValue, "unit": currentUnit["name"], "orginalText": orginalText.strip()}})

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
                    currentUnit = nutrient['defaultUnit']

                # Unit is an object containing a lot of data, for now we only use the name
                if currentUnit:
                    currentUnit = currentUnit["name"]
                # Add the data
                arrayToReturn.append({"name": nutrient["nutrient"]["name"], "code": None, "amount": {
                                     "value": currentValue, "unit": currentUnit, "orginalText": orginalText.strip()}})
            # Break as max depth reased
            break

    return arrayToReturn


"""
Cannot use this as there is no per data in the data :(

def makePerData(array):
    if array == None or len(array) == 0:
        return
    
    # Make new object, Name must be text because data is appended to it
    data = {"per": {"name": "", "value": None, "unit": None, "orginalText": None}, "prepared": False, "rows": []}

    # Set vars
    orginalText = ""
    maxDepthToGo = 4

    # Loop over all words
    for word in array:
        print(word)
        orginalText += " " + word

        # Check if Value and if no value is set yet
        possibleValue = indentifyValue(word)
        if possibleValue and data['per']['value'] == None:
            # Set data
            data['per']['value'] = possibleValue
            data['per']['name'] = possibleValue + data['per']['name']
            # Remove bit from word is the unit is glued to the value
            word = regexSub('^[0-9]+(.[0-9])?', '', word)

        # Check if Unit and if no unit is set yet
        possibleUnit = indentifyUnit(word)
        if possibleUnit and data['per']['unit'] == None:
            # Set data
            data['per']['unit'] = possibleUnit['notation']
            data['per']['name'] = data['per']['name'] + " " + possibleUnit['name']

        # Check if all data is set meaning it can end
        if data['per']['value'] != None and data['per']['unit'] != None:
            # Set data
            data['per']['orginalText'] = orginalText
            # Fix data if needed
            if data['per']['name'] == "":
                data['per']['name'] = None
            # Return data and the amount of words used to indentify it
            return data

        # Keep track of the max depth it can go
        maxDepthToGo -= 1
        # If max depth is reased or the end of the array, lets go back
        if maxDepthToGo == 0:
            return None
    return None


def checkForPerData(array, data, language="NL"):
    print(array)
    # Identify if per trigger
    for i, word in enumerate(array):
        if identifyPer(word, language):
            # Return new per data
            newPerData = makePerData(array[i:])
            if newPerData:
                return data['data'].append(newPerData['data'])
        else:
            return None
    else:
        return None


def delete_useless_data(data):
    return data[loop_over_per_data(data):]


def loop_over_per_data(data):
    for i, row in enumerate(data):
        for text in row:
            if text == None:
                continue
            array = text.split(r'\s')
            for a in array:
                if identifyPer(a):
                    return i
    return 0
"""
