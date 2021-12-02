import re as regex


def regexMatch(reg, string):
    # Force exact match over the enitre string using regex
    return regex.match("^("+reg+")$", regex.sub('\(|\)', '', string.strip()), regex.IGNORECASE)


def regexSearch(reg, string):
    return regex.search(reg, string, regex.IGNORECASE)


def regexSub(reg, replaceString, string):
    return regex.sub(reg, replaceString, string)
