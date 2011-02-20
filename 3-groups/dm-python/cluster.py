from math import sqrt
from numpy import mean
import random
from PIL import Image, ImageDraw

class bicluster:
    def __init__(self, vec, left=None, right=None, error=0.0, name=""):
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

class multicluster:
    def __init__(self, vec, children=None, error = 0.0, name=""):
        self.vec = vec
        self.children = children
        self.error = error
        self.name = name
    def __str__(self):
        if self.children == None:
            return str("-" + self.name)
        elif len(self.children) == 0:
            return "empty cluster"
        else:
            firstChildRep = str(self.children[0]).splitlines()
            buildStr = ["-+" + firstChildRep[0]]
            buildStr.extend([" |" + line for line in firstChildRep[1:]])
            if len(self.children)==1: return '\n'.join(buildStr)
            for child in self.children[1:-1]:
                rep = str(child).splitlines()
                buildStr.append(" +"+rep[0])
                buildStr.extend([" |"+line for line in rep[1:]])
            lastChildRep = str(self.children[-1]).splitlines()
            buildStr.append(" \\"+lastChildRep[0])
            buildStr.extend(["  "+line for line in lastChildRep[1:]])
            return '\n'.join(buildStr)


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
    if den>0:
        return 1.0 - num/den
    else: return 0.0


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

def getWidth(cluster):
    """
    The width of a cluster is 1 if it has no children, and is
    otherwise the sum of the widths of its branches.
    """
    if cluster.left == None and cluster.right == None: return 1
    return getWidth(cluster.left) + getWidth(cluster.right)

def getDepth(cluster):
    """
    The depth of a cluster is 0 if it is a leaf, or cluster.error plus
    the maximum depth of its children.
    """
    if cluster.left == None and cluster.right == None: return 0.0
    return max(getDepth(cluster.left),getDepth(cluster.right)) + cluster.error

def drawDendrogram(cluster, file="dendrogram.jpg"):
    """
    Given a cluster, outputs a dendrogram depiction of that cluster as
    a jpg image.  The lengths of the lines depicting a pair of
    children are proportional to the degree of dissimilarity between
    the pair.
    """

    imageHeight = getWidth(cluster) * 20
    imageWidth = 1200

    clusterDepth = getDepth(cluster)

    scaling = float(imageWidth-150)/clusterDepth

    # Create a new image with a white background
    img = Image.new('RGB',(imageWidth,imageHeight), (255,255,255))
    draw = ImageDraw.Draw(img)

    # Draw the dendrogram
    draw.line((0,imageHeight/2,10,imageHeight/2), fill=(0,0,0))
    drawNode(draw, cluster, 10, imageHeight/2, scaling)

    # Save the image
    img.save(file,'JPEG')

def drawNode(draw, cluster, x, y, scaling):
    """
    Given a DrawImage 'draw', and cluster 'cluster', draw the
    dendrogram representing the cluster with its root located at x,y.
    """
    if cluster.left == None and cluster.right == None:
        # Draw a leaf node (i.e. just print the label)
        draw.text((x+5,y-7),cluster.name,(0,0,0))
    else:
        # Draw a branch node
        h1 = getWidth(cluster.left) * 20
        h2 = getWidth(cluster.right) * 20
        branchLength = cluster.error * scaling
        y0 = y - h2/2
        y1 = y + h1/2

        draw.line((x,y0,x,y1), fill=(0,0,0))
        draw.line((x,y0,x+branchLength,y0), fill=(0,0,0))
        draw.line((x,y1,x+branchLength,y1), fill=(0,0,0))
        drawNode(draw, cluster.left, x+branchLength, y0, scaling)
        drawNode(draw, cluster.right, x+branchLength, y1, scaling)

def kMeansCluster(rowNames, data, numClusters = 4, distance = pearsonSimilarity, merge = lambda mc:mean([child.vec for child in mc],0), maxIters = 100):
    """kMeansCluster(rowNames, data, numClusters, distance, merge, maxIters) -> multicluster

    Performas K-Means clustering with numClusters clusters (default of
    4), using the distance measure 'distance' (default is
    pearsonSimilarity) using 'merge' to calculate the position of a
    multicluster (default is the mean of the vectors of its children).

    Keep iterating the k-Means algorithm until there are no changes in
    cluster assignments or we reach maxIters (default = 100) iterations.
    """
    # Calculate the range of values for each feature; needed in order
    # to seed our cluster positions.
    ranges = [(min([row[i] for row in data]),max([row[i] for row in data])) for i in range(len(data[0]))]

    # Randomly initialise the positions of the numCluster clusters;
    # these are simply represented as vectors of values throughout the
    # function, and converted to multiclusters at the end.
    clusters = [[
        random.random()*(ranges[i][1]-ranges[i][0]) + ranges[i][0]
        for i in range(len(data[0]))
    ] for j in range(numClusters)]

    # Construct the leaf clusters
    leafs = [multicluster(row, name=title) for (row, title) in zip(data, rowNames)]

    lastAssignment = None
    for iter in range(maxIters):
        print 'Iteration %d (max %d)' % (iter + 1, maxIters)
        bestAssignment = [[] for i in range(numClusters)]

        for leaf in leafs:
            bestMatch = 0
            bestd = distance(clusters[0], leaf.vec)
            for i in range(1,numClusters):
                d = distance(clusters[i], leaf.vec)
                if d<bestd:
                    bestMatch = i
                    bestd = d
            bestAssignment[bestMatch].append(leaf)

        if bestAssignment == lastAssignment: break
        lastAssignment = bestAssignment

        newClusters = []
        for cluster, kids in zip(clusters, bestAssignment):
            if len(kids) == 0:
                newCluster = cluster
            else:
                newCluster = merge(kids)
            newClusters.append(newCluster)

        clusters = newClusters
    # construct and return the result as a list of multiclusters
    return [multicluster(vec, children=kids) for (vec, kids) in zip(clusters, bestAssignment)]


def loadData(fileName):
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
