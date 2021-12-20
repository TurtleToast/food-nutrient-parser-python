import lxml.html

from nutrients_parser.functions.identifiers import identifyValue, identifyNutrient, identifyPer
from ..functions.regex import *
from pprint import pprint


def parse_htmldata(html, language="NL"):
    data = parse_html_tablelike(html, language=language)
    #data = normalize_all(data)
    return data

# TODO handle colspan and rowspan (expand them to single cells)
#      e.g. https://www.sainsburys.co.uk/gol-ui/product/potatoes/sainsburys-baking-potatoes-loose


def parse_html_tablelike(html, language="NL"):
    doc = lxml.html.fromstring(html)
    
    return extract_nutrientvalue_data(doc, language=language), extract_per_data(doc, language=language)

def extract_nutrientvalue_data(doc, language = "NL"):
    # We look for elements with two or more nutrient names.
    # Their closest common ancestor is assumed to be the 'tbody'.
    #nutrients = find_text_re(doc, nutrient_names_re, exact=True)
    nutrients = find_nutrient_text(doc, exact = False, language=language)
    if len(nutrients) == 0:
        print("No nutrients found")
        return
    elif len(nutrients) == 1:
        print("Only one nutrient found, need at least two.")
        return
    nutrient_depth = len(get_el_path(nutrients[0]))

    tbody = find_strongest_common_ancestor(nutrients)
    if tbody is None:
        print("Could not identify nutrients body")
        return
    tbody_depth = len(get_el_path(tbody))

    # Then we look for nutrient values within the 'tbody'.
    # Reject any numbers that look like nutrients (e.g. B6)
    #values = find_text_re(tbody, numeric_values_re)
    values = find_value_text(tbody, exact = False)
    values = list(
        filter(lambda v: not identifyNutrient(stringArray = v.text), values))
    if len(values) == 0:
        print("No nutrient value found")
        return
    value_depth = most_common([len(get_el_path(v)) for v in values])

    # Find the closest ancestor in all nutrient-value combinations.
    # Its depth is assumed to be the level of a 'tr'.
    tr_sample = find_common_ancestor_combination(nutrients, values)
    if tr_sample is None:
        print("Could not identify nutrient row")
        return
    tr_depth = len(get_el_path(tr_sample))

    # When nutrients and values are on the same level, we take the
    # highest level, so that when some text is in an 'em' tag or so,
    # we still get the full text.
    td_depth = min(nutrient_depth, value_depth)

    #print('tbody', tbody_depth, 'tr', tr_depth, 'td', td_depth, 'td.nut', nutrient_depth, 'td.val', value_depth)

    rows = []
    for row in tbody.xpath(('*/' * (tr_depth - tbody_depth)).rstrip('/')):
        if td_depth > tr_depth:
            # get cells from the row
            cells = row.xpath(('*/' * (td_depth - tr_depth)).rstrip('/'))
            rows.append([remove_white_spaces(''.join(c.itertext()))
                        for c in cells])
        else:
            # in a list, the row may directly contain the nutrient
            rows.append([row.text] + [c.text_content()
                        for c in row.getchildren()])

    # No need for stripping whitespaces, happens already above, only replace empty strings with None
    for i, row in enumerate(rows):
        rows[i] = [c if c else None for c in row]
    
    return rows

def extract_per_data(doc, language = "NL"):
    pers = find_per_text(doc, language=language)
    if len(pers) == 0:
        print("No per data found")
        return
    per_depth = len(get_el_path(pers[0]))

    thead = find_strongest_common_ancestor(pers)
    if thead is None:
        print("Could not identify per body")
        return
    thead_depth = len(get_el_path(thead))

    perRows = []
    path = thead.xpath(('*/').rstrip('/'))
    if len(path) == 0:
        perRows.append([remove_white_spaces(thead.text_content())])
    else:
        for row in thead.xpath(('*/').rstrip('/')):
            if thead_depth > per_depth:
                # get cells from the row
                cells = row.xpath(('*/').rstrip('/'))
                perRows.append([remove_white_spaces(''.join(c.itertext()))
                            for c in cells])
            else:
                # in a list, the row may directly contain the nutrient
                perRows.append([row.text] + [c.text_content()
                            for c in row.getchildren()])
    
    return perRows

def remove_white_spaces(string):
    # Simple regex sub to remove whitespaces
    return regexSub("\s", " ", string).strip()


def find_nutrient_text(sel, exact=False, language="NL"):
    if exact:
        return [el for el in sel.xpath('//*[boolean(text())]') if el.text and identifyNutrient(string=el.text, language=language)]
    else:
        return [el for el in sel.xpath('//*[boolean(text())]') if el.text and identifyNutrient(stringArray=el.text, language=language)]


def find_value_text(sel, exact=False):
    if exact:
        return [el for el in sel.xpath('//*[boolean(text())]') if el.text and identifyValue(string=el.text, exact=True)]
    else:
        return [el for el in sel.xpath('//*[boolean(text())]') if el.text and identifyValue(string=el.text)]


def find_per_text(sel, language = "NL"):
    return [el for el in sel.xpath('//*[boolean(text())]') if el.text and identifyPer(string=el.text, language = language)]


def get_el_path(el):
    """
    Returns itself and its ancestors.

    >>> import lxml.html
    >>> doc = lxml.html.fromstring('<html><body><h1>Hi <em>there</em></h1><p>Bye.</p></body></html>')
    >>> path = get_el_path(doc.xpath('//em')[0])
    >>> [p.tag for p in path]
    ['em', 'h1', 'body', 'html']
    """
    parents = []
    cur = el
    while cur is not None:
        parents.append(cur)
        cur = cur.getparent()
    return parents


def find_common_ancestor(els):
    """
    Returns the deepest common ancestor of all elements.

    >>> import lxml.html
    >>> doc = lxml.html.fromstring('<table><tbody><tr><td>A</td><td>B</td></tr></tbody></table>')
    >>> find_common_ancestor(doc.xpath('//td')).tag
    'tr'

    >>> doc = lxml.html.fromstring('<div><table><tbody><tr><td><em>A</em></td><td><em>B</em></td></tr></tbody></table><em>C</em></div>')
    >>> find_common_ancestor(doc.xpath('//em')).tag
    'div'
    """
    common_parents = get_el_path(els[0])

    for el in els:
        el_parents = get_el_path(el)
        common_parents = [p for p in common_parents if p in el_parents]

    if len(common_parents) > 0:
        return common_parents[0]
    else:
        return None


def find_strongest_common_ancestor(els):
    """
    Return the deepest common ancestor of all elements, provided that
    at least 2/3 of the elements have this ancestor.

    >>> import lxml.html
    >>> doc = lxml.html.fromstring('<table><tbody><tr><td>A</td><td>B</td></tr></tbody></table>')
    >>> find_strongest_common_ancestor(doc.xpath('//td')).tag
    'tr'

    >>> import lxml.html
    >>> doc = lxml.html.fromstring('<div><table><tbody><tr><td><em>A</em></td><td><em>B</em></td></tr></tbody></table><em>C</em></div>')
    >>> find_strongest_common_ancestor(doc.xpath('//em')).tag
    'tr'
    """
    if len(els) == 1:
        return els[0]

    ancestors = dict()

    # gather all ancestors
    for el in els:
        for a in get_el_path(el)[1:-1]:
            if a not in ancestors:
                ancestors[a] = [(len(a), el)]
            else:
                ancestors[a].append((len(a), el))

    # reject ancestors with less than 2/3 of the elements
    qualifying_ancestors = []
    for a, aeltuples in ancestors.items():
        if 3 * len(aeltuples) >= 2 * len(els):
            qualifying_ancestors.append((a, aeltuples))

    # sort by element depth
    qualifying_ancestors.sort(key=lambda a: max(
        *[t[0] for t in a[1]]), reverse=True)

    if len(qualifying_ancestors) > 0:
        return qualifying_ancestors[0][0]
    else:
        return None


def find_common_ancestor_combination(a, b):
    """
    Return the deepest common ancestor of any combination of elements between a and b.

    >>> import lxml.html
    >>> doc = lxml.html.fromstring('<table><tbody><tr><td>A</td><td>B</td></tr><tr><td>C</td><td>D</td></tr></tbody></table>')
    >>> find_common_ancestor_combination(doc.xpath('//*[text()="A"]'), doc.xpath('//*[text()="B"]')).tag
    'tr'
    >>> find_common_ancestor_combination(doc.xpath('//*[text()="A" or text()="B"]'), doc.xpath('//*[text()="B"]')).tag
    'td'
    >>> find_common_ancestor_combination(doc.xpath('//*[text()="A" or text()="B"]'), doc.xpath('//*[text()="C"]')).tag
    'tbody'

    >>> doc = lxml.html.fromstring('<table><caption>B</caption><tbody><tr><td>A</td><td>B</td></tr><tr><td>A</td><td>B</td></tr></tbody></table>')
    >>> find_common_ancestor_combination(doc.xpath('//*[text()="A"]'), doc.xpath('//*[text()="B"]')).tag
    'tr'
    """
    paths_a = [get_el_path(el) for el in a]
    paths_b = [get_el_path(el) for el in b]
    strongest_common = None

    for path_a in paths_a:
        for path_b in paths_b:
            common = [p for p in path_a if p in path_b]
            if strongest_common is None or len(common) > len(strongest_common):
                strongest_common = common

    return strongest_common[0]

# http://stackoverflow.com/questions/1518522


def most_common(lst):
    return max(set(lst), key=lst.count)
