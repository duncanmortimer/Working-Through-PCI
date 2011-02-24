from math import sqrt

def pearson_dist(v1, v2):
    n = float(len(v1))
    sum_1 = sum(v1)
    sum_2 = sum(v2)
    sum_sq_1 = sum([pow(v, 2) for v in v1])
    sum_sq_2 = sum([pow(v, 2) for v in v2])
    sum_prod = sum([v1[i]*v2[i] for i in range(int(n))])

    num = sum_prod - sum_1*sum_2/n
    den = sqrt((sum_sq_1 - sum_1*sum_1/n) * (sum_sq_2 - sum_2*sum_2/n))
    if den == 0:
        return 0
    else:
        return 1.0 - num/den

class Bicluster(object):
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec =vec
        self.id = id
        self.distance = distance

def cluster_hierarchy(vectors, distance=pearson_dist):
    """
    Calculate the cluster hierarchy of the given vectors using indices
    as IDS.
    """

    next_new_cluster_id = -1 # Use negative indices for new clusters
    distances = {}
    clusters = [Bicluster(v, id=i) for i, v in enumerate(vectors)]

    while len(clusters) > 1:
        (left_index, right_index) = 0, 1
        closest = distance(clusters[0].vec, clusters[1].vec)

        for i, ca in enumerate(clusters):
            for j, cb in enumerate(clusters[i+1:], i+1):
                if (ca.id, cb.id) not in distances:
                    distances[(ca.id, cb.id)] = distance(ca.vec, cb.vec)

                if closest > distances[(ca.id, cb.id)]:
                    closest = distances[(ca.id, cb.id)]
                    left_index, right_index = i, j

        cluster_right = clusters.pop(right_index)
        cluster_left = clusters.pop(left_index)

        # Calculate new cluster
        avg_vec = [(cluster_left.vec[i] + cluster_right.vec[i])/2.0
                   for i in range(len(cluster_left.vec))]

        clusters.append(Bicluster(avg_vec, distance=closest,
                                  left=cluster_left, right=cluster_right,
                                  id=next_new_cluster_id))
        next_new_cluster_id -= 1

    return clusters[0]

def cluster_list(clust):
    if clust.id <= -1:
        return cluster_list(clust.left) + cluster_list(clust.right)
    else:
        return [clust]

def print_cluster(clust, labels=None, n=0):
    print ' '*n,

    if clust.id < 0:
        print '-'
    elif labels == None:
        print clust.id
    else:
        print labels[clust.id]

    if clust.left != None:
        print_cluster(clust.left, labels=labels, n=n+1)
    if clust.right != None:
        print_cluster(clust.right, labels=labels, n=n+1)
