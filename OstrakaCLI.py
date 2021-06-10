from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from Pot import Pot
from Boule import Boule
import sys
import os
import socket
from p2pnetwork.node import Node

wd = os.path.abspath(os.getcwd())
path = wd + "/OstrakaData"

def getDataFolder ():
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
        if not os.path.isdir(dataFldr):
            print("Creating default folder")
            os.mkdir(dataFldr)

    return dataFldr

def getPot (dataFldr):
    potsFldr = dataFldr + "/Pots/"
    if not os.path.isdir(potsFldr):
        print("Creating pots folder")
        os.mkdir(potsFldr)

    newPot = "Create a new Pot"
    availablePots = os.listdir(potsFldr)
    availablePots.append(newPot)

    questions = [
        {
            'type': 'list',
            'name': 'which_pot',
            'message': 'Choose a Pot:',
            'choices': availablePots
        }
    ]

    answers = prompt(questions)
    if answers["which_pot"] == newPot:
        myPot = Pot()

        questions = [
            {
                'type': 'input',
                'name': 'pot_name',
                'message': 'Specify new pot nick name:'
            }
        ]

        answers = prompt(questions)
        potName = answers['pot_name']
        f = open(potsFldr + potName + '.pot', 'w')
        f.write(myPot.export_key())
        f.close()
    else:
        potName = answers["which_pot"]
        f = open(potsFldr + potName, 'r')
        myPot = Pot(f.read())
        f.close()

        print(myPot.get_public_key())

    return myPot

# node = Node("127.0.0.1", 8001, None)



def getBoule (dataFldr):
    boulesFldr = dataFldr + "/Boules/"
    if not os.path.isdir(boulesFldr):
        print("Creating boules folder")
        os.mkdir(boulesFldr)

    foundBoule = "Found a new Boule"
    findBoule = "Connect to an existing Boule"
    availableBoules = os.listdir(boulesFldr)
    availableBoules.extend([foundBoule, findBoule])

    questions = [
        {
            'type': 'list',
            'name': 'which_boule',
            'message': 'Choose a Boule:',
            'choices': availableBoules
        }
    ]

    answers = prompt(questions)

    if answers['which_boule'] == findBoule:
        questions = [
            {
                'type': 'input',
                'name': 'node_ip',
                'message': 'Enter existing Boule node IP address:'
            }
        ]

        answers = prompt(questions)
        ip = answers['node_ip']
        print('cannot work with this yet')
    
    elif answers['which_boule'] == foundBoule:
        questions = [
            {
                'type': 'input',
                'name': 'boule_name',
                'message': 'Enter name for new Boule:'
            }
        ]

        answers = prompt(questions)
        bouleName = answers['boule_name']
        print(getIP())
    

df = getDataFolder()
pot = getPot(df)
boule = getBoule(df)