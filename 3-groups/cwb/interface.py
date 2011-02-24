#!/usr/bin/env python

import os
from bottle import route, run, debug, static_file, template
import random

RESOURCES = os.path.abspath("../../resources")

@route('/js/:filename')
def server_static(filename):
    return static_file(filename, root=os.path.join(RESOURCES, 'js'))

ROOT = os.path.dirname(os.path.abspath(__file__))

import data
import groups

@route('/blogdata/:clustered#(|cluster)#')
def blogdata(clustered=False):
    def dict_clusters(clust):
        count = dict(zip(cols, matrix[clust.id]))
        count.update({'Blog': rows[clust.id]})
        return count

    rows, cols, matrix = data.get_data('blogdata.txt')

    if clustered:
        print "Calculating clusters...",
        clusters = groups.cluster_list(groups.cluster_hierarchy(matrix))
        print " DONE."
        counts = map(dict_clusters, clusters)
    else:
        counts = []
        for i, vector in enumerate(matrix):
            d = dict(zip(cols, vector))
            d.update({'Blog': rows[i]})
            counts.append(d)

    return {"cols": cols, "counts": counts}

@route('/blogmatrix/:clustered#(|cluster)#')
def blogmatrix(clustered=''):
    return template('matrix', data_url='/blogdata/'+clustered)

if __name__ == '__main__':
    debug(True)
    run(host='localhost', port=8080, reloader=True)
