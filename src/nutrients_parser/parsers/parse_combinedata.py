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
    ]
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
        'rows': [
            {
                'amount': {
                    'orginalText': 'kJ 577',
                    'unit': 'Kilojoules',
                    'value': '577'
                },
                'code': None,
                'name': 'energie'
            },
            {
                'amount': {
                    'orginalText': 'kcal 137',
                    'unit': 'Calories',
                    'value': '137'
                },
                code': None,
                'name': 'energie'
            },
            {
                'amount': {
                    'orginalText': '4.4',
                    'unit': 'Gram',
                    'value': '4.4'
                },
                'code': None,
                'name': 'vetten'
            }
        ]
    },
    {'per':
        {
            'name': '450 Gram',
            'orginalText': 'Per 450 g:',
            'unit': 'g',
            'value': '450'
        },
        'prepared': False,
        'rows': [
            {
                'amount': {
                    'orginalText': 'kJ 2596',
                    'unit': 'Kilojoules',
                    'value': '2596'
                },
                'code': None,
                'name': 'energie'
            },
            {
                'amount': {
                    'orginalText': 'kcal 617',
                    'unit': 'Calories',
                    'value': '617'
                },
                code': None,
                'name': 'energie'
            },
            {
                'amount': {
                    'orginalText': '19.8',
                    'unit': 'Gram',
                    'value': '19.8'
                },
                'code': None,
                'name': 'vetten gram'
            }]
    }
]

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


def parse_combinedata(dataRows, perData):
    for row in dataRows:
        nutrient = row[0][0]
        for i, value in enumerate(row[1]):
            if len(perData) >= i + 1:
                for x in value:
                    perData[i]['rows'].append({"name": nutrient,  "code": None,  "amount":x})
    return perData