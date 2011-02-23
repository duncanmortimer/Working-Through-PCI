#!/usr/bin/env python

import os
from bottle import route, run, debug, static_file
import random

RESOURCES = os.path.abspath("../../resources")

@route('/js/:filename')
def server_static(filename):
    return static_file(filename, root=os.path.join(RESOURCES, 'js'))

ROOT = os.path.dirname(os.path.abspath(__file__))

@route('/')
def index():
    return static_file('interface.html', root=ROOT)

@route('/data')
def data():
    return {"points": [{'x': random.random(),
                        'y': random.random()} for i in range(100)]}

import data

@route('/blogdata')
def show():
    counts = data.get_data('blogdata.txt')
    return {"cols": counts[0].keys(), "counts": counts}

@route('/blogmatrix')
def index():
    return static_file('matrix.html', root=ROOT)

if __name__ == '__main__':
    debug(True)
    run(host='localhost', port=8080, reloader=True)
