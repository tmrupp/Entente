from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from Pot import Pot
import sys
import os

wd = os.path.abspath(os.getcwd())
path = wd + "/OstrakaData"
exists = os.path.isdir(path)

diffFldr = 'Use external data folder'
defaultFldr = 'Use default data folder'

dataFldr = ''

questions = [
    {
        'type': 'list',
        'name': 'data_folder',
        'message': 'Load Ostraka data:',
        'choices': [diffFldr, defaultFldr]
    }
]

answers = prompt(questions)

if answers['data_folder'] == diffFldr:
    questions = [
        {
            'type': 'input',
            'name': 'external_path',
            'message': 'Specify external path:'
        }
    ]

    answers = prompt(questions)
    dataFldr = answers['external_path']
else:
    dataFldr = path
    if not os.path.isdir(path):
        print("Creating default folder")
        os.mkdir(path)







    
    
    