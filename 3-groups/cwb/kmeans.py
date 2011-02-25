import random
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
