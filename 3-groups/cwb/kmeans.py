import random
from math import sqrt
from groups import pearson_dist

# Usage:
# >>> rows, cols, data = data.get_data('blogdata.txt')
# >>> clusters = cluster_kmeans(vectors, k=10)
# >>> [[rows[id] for id in clusters[j]] for j in range(len(clusters))]

def cluster_kmeans(vectors, k=5, distance=pearson_dist):
    n = len(vectors[0])
    # Determine the minimum and maximum values for each point
    ranges = [(min([v[i] for v in vectors]),
               max([v[i] for v in vectors])) for i in range(n)]

    # Create k randomly placed centroids
    clusters = [[random.randrange(ranges[j][0], ranges[j][1], int=float)
                 for j in range(n)] for i in range(k)]

    previous_memberships = None

    for t in range(20): # Stop after 20 iterations regardless
        print 'Iteration %d' % t

        # Represent vector belongings by a list of sets containing
        # vector indices to indicate which cluster the vector is
        # closest to. For example, if vector with index 3 belongs to
        # cluster 2 (1-indexed) we'd have: [set(..), set([.., 2, ..]),
        # set(..)]

        memberships = [set() for i in range(k)]

        # So, loop each vector and put in appropriate list
        for id, vector in enumerate(vectors):
            distances = [(i, distance(cluster, vector))
                         for i, cluster in enumerate(clusters)]
            closest_cluster, _ = min(distances, key=lambda x: x[1])
            memberships[closest_cluster].add(id)

        # Break if memberships haven't changed
        if memberships == previous_memberships: break
        previous_memberships = memberships

        # Adjust cluster centroids
        for i in range(k):
            member_vectors = [vectors[j] for j in memberships[i]]
            members = float(len(member_vectors))
            if members > 0:
                clusters[i] = [sum([v[l] for v in member_vectors])/members
                               for l in range(n)]

    return memberships

def scaledown(data, distance=pearson_dist, rate=0.01):
    r = len(data)
    c = len(data[0])

    # Calculate all real distances (inefficiently)
    real_dists = [[distance(data[i], data[j]) for j in range(r)]
                  for i in range(r)]

    # Randomly allocate starting points
    locs = [[random.random(), random.random()] for i in data]
    fake_dists = [[0.0 for j in range(r)] for i in range(r)]

    lasterror = None
    for m in range(1000): # Stop after 1000 iteration regardless
        print "Iteration %d" % m

        # Find projected distances
        for i in range(r):
            for j in range(r):
                fake_dists[i][j] = sqrt(sum([pow(locs[i][x]-locs[j][x],2)
                                             for x in range(len(locs[i]))]))

        # Move points
        grad=[[0.0, 0.0] for i in range(r)]
        totalerror = 0
        for i in range(r):
            for j in range(r):
                if i==j: continue
                error = (fake_dists[i][j]-real_dists[i][j])/real_dists[i][j]
                grad[i][0] += ((locs[i][0]-locs[j][0])/fake_dists[j][i])*error
                grad[i][1] += ((locs[i][1]-locs[j][1])/fake_dists[j][i])*error
                totalerror += abs(error)

        print "Error: %.5f" % totalerror
        if lasterror and lasterror < totalerror: break
        lasterror = totalerror

        # Move each of the points by the learning rate times the
        # gradient
        for i in range(r):
            locs[i][0] -= rate*grad[i][0]
            locs[i][1] -= rate*grad[i][1]

    return locs

import json

def save_scaledown(data, filename):
    locs = scaledown(data)
    f = file(filename, "w")
    json.dump(locs, f)
    f.close()

def load_scaledown(filename):
    f = file(filename, "r")
    data = json.load(f)
    f.close()
    return data
