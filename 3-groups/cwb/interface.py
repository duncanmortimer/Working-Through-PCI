#!/usr/bin/env python

import os
from bottle import route, run, debug, static_file, template, validate
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

@route('/dendrodata/')
def dendrodata():
    rows, cols, matrix = data.get_data('blogdata.txt')

    print "Calculating clusters...",
    tree = groups.cluster_dict(groups.cluster_hierarchy(matrix), rows)
    print " DONE."

    return {"tree": tree}

@route('/blogdendro/')
def blogmatrix():
    return template('dendro', data_url='/dendrodata/')

import kmeans

@route('/data/kmeans/:k#[0-9]+#')
@validate(k=int)
def data_kmeans(k=5):
    rows, cols, matrix = data.get_data('blogdata.txt')
    # Cluster data
    clusters = kmeans.cluster_kmeans(matrix, k=k)
    cluster_dict = {}

    for k, cluster in enumerate(clusters):
        for i in cluster:
            cluster_dict[i] = k

    # Load blog locations in 2d
    locations = kmeans.load_scaledown('bloglocs.json')
    minimum = min([x[0] for x in locations] + [x[1] for x in locations])
    maximum = max([x[0] for x in locations] + [x[1] for x in locations])

    # Create points
    points = [{'name': rows[i],
               'x': locations[i][0],
               'y': locations[i][1],
               'cluster': cluster_dict[i]} for i in range(len(rows))]

    return {"points": points,
            'minimum': minimum,
            'maximum': maximum}

@route('/blog/kmeans/:k#[0-9]+#')
def blog_kmeans(k=5):
    return template('kmeans', data_url='/data/kmeans/'+str(int(k)))

if __name__ == '__main__':
    debug(True)
    run(host='localhost', port=8080, reloader=True)
