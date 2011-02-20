from math import sqrt

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
