from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from Pot import Pot
import sys
import os

wd = os.path.abspath(os.getcwd())
path = wd + "/OstrakaData"
exists = os.path.isdir(path)

newFldr = 'Create new data folder'
diffFldr = 'Specify external data folder path'
defaultFldr = 'Use existing default folder'

dataFldr = ''

options = [
    newFldr,
    diffFldr,
]

if exists:
    options.append(defaultFldr)

questions = [
    {
        'type': 'list',
        'name': 'data_method',
        'message': 'Select data to load:',
        'choices': options
    }
]

answers = prompt(questions)

if answers['data_method'] == newFldr:

    newNewFldr = 'Specify new data folder path'
    newDefaultFldr = 'Create folder at default location (./OstrakaData/)'

    options = [newNewFldr]
    if not exists:
        options.append(newDefaultFldr)

    questions = [
        {
            'type': 'list',
            'name': 'new_fldr_loc',
            'message': 'Select where to create data folder:',
            'choices': options
        }
    ]
    
    answers = prompt(questions)
    newDataPath = './OstrakaData/'
    if answers['new_fldr_loc'] == newNewFldr:
        q = [{
            'type' : 'input',
            'name' : 'loc',
            'message' : 'Input path to new data folder:'
        }]

        answers = prompt(q)

        newDataPath = answers['loc']

    os.mkdir(newDataPath)
    dataFldr = newDataPath

elif answers['data_method'] == diffFldr:
    



