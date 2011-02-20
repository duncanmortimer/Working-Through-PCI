from math import sqrt
from numpy import mean

def loadData(filename):
    """loadData(fileName) -> rowNames, colNames, data

    Given a text file containing a tab-separated table of data to
    cluster, with the first row the names of the fields and first
    column the names of the entities, return a matrix (represented as
    a list of lists) of values, along with a list of entity and field
    names.
    """
    f = file(fileName)

    colNames = f.readline().strip().split('\t')[1:]

    rowNames = []
    data = []
    for line in f:
        theData = line.strip().split('\t')
        rowNames.append(theData[0])
        data.append([float(d) for d in theData[1:]])
    return rowNames, colNames, data

def pearsonSimilarity(v1,v2):
    """
    Calculate the pearson similarity for v1 and v2 (i.e. 1.0 minus the
    Pearson correlation coefficient between vectors v1 and v2).
    """

    v1dotv2 = sum([e1*e2 for (e1,e2) in zip(v1, v2)])
    v1dotv1 = sum([e**2 for e in v1])
    v2dotv2 = sum([e**2 for e in v2])
    sumv1 = sum(v1)
    sumv2 = sum(v2)
    n = len(v1)

    num = v1dotv2 - sumv1*sumv2/n
    den = sqrt((v1dotv1 - sumv1**2/n)*(v2dotv2 - sumv2**2/n))
    return 1.0 - num/den

class bicluster:
    def __init__(self, vec, left=None, right=None, error=0.0, name=None):
        self.vec = vec
        self.left = left
        self.right = right
        self.error = error
        self.name = name
    def __str__(self):
        if self.left == None:
            return str("-" + self.name)
        else:
            leftRep = str(self.left).splitlines()
            rightRep = str(self.right).splitlines()
            buildStr = ["-+" + leftRep[0]]
            buildStr.extend([" |" + line for line in leftRep[1:]])
            buildStr.append(" \\" + rightRep[0])
            buildStr.extend(["  " + line for line in rightRep[1:]])
            return '\n'.join(buildStr)

def hierCluster(rowNames, data, distance=pearsonSimilarity, merge=lambda v1, v2: mean([v1,v2], 0)):
    """hierCluster(rowNames, data, distance=pearsonSimilarity) -> bicluster

    Cluster 'data' (with rows corresponding to items with names
    'rowNames') using the hierarchical clustering algorithm.  By
    default, use the pearson similarity measure as the distance
    measure, and clusters are merged by taking the pointwise mean of
    their constituent data.
    """

    # The 'distances' dictionary is used to memoize the calculation of
    # distances between clusters.
    distances = {}

    clusters = [bicluster(row, name=title) for (row, title) in
                zip(data, rowNames)]

    # We now repeatedly merge the nearest pair of clusters in
    # 'clusters' until only one cluster remains
    while len(clusters) > 1:
        # find the closest pair of clusters:
        nearestPair = (0,1)
        nearestDistance = distance(clusters[0].vec, clusters[1].vec)

        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                pairId = (id(clusters[i]), id(clusters[j]))

                try:
                    d = distances[pairId]
                except KeyError:
                    d = distance(clusters[i].vec,clusters[j].vec)
                    distances[pairId] = d

                if d<nearestDistance:
                    nearestDistance = d
                    nearestPair = (i,j)

        # now have nearest pair of clusters; need to merge them
        leftInd = nearestPair[0]
        rightInd = nearestPair[1]

        mergedCluster = bicluster(merge(clusters[leftInd].vec,clusters[rightInd].vec), left=clusters[leftInd], right=clusters[rightInd], error = nearestDistance)

        # remove the nearest pair from the list of clusters
        del clusters[rightInd]
        del clusters[leftInd]
        clusters.append(mergedCluster)
    return clusters[0]
