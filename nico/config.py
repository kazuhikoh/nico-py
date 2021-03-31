import os
import json

def load():
    home = os.environ['HOME']
    f = open(f'{home}/.nico.json', 'r')
    j = json.load(f)
    return j
