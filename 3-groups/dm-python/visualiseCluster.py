from PIL import Image, ImageDraw
from numpy import sqrt
from cluster import getWidth, getDepth

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

def drawScaleDown(scaleResults, projection = None, width = 1000, height = 1000, relativeMargin = 0.05, withHierCluster = False, jpeg = "scaledown.jpg"):
    """
    Generates a jpg image showing the results from the scaleDown
    algorithm.  If more than two dimensions were used, the results are
    projected onto the plane defined by the pair of vectors in the
    tuple 'projection' (= (v1, v2)).  By default, just project onto
    the first 2 components.
    """
    dim = len(scaleResults[0][1])

    # If projection = None, calculate the principle components of
    # scaleResults
    if projection is None:
        v = [0]*dim
        v1=list(v); v1[0] = 1
        v2=list(v); v2[1] = 1

    # Convert projection = (v1,v2) into an orthonormal basis
    absv1 = sqrt(sum([v1[d]**2 for d in range(dim)]))
    v1 = [v/absv1 for v in v1]
    dotv1v2 = sum([v1[d]*v2[d] for d in range(dim)])
    v2 = [v2[d] - dotv1v2*v1[d] for d in range(dim)]
    absv2 = sqrt(sum([v2[d]**2 for d in range(dim)]))
    v2 = [v/absv2 for v in v2]

    # Project the data onto the vectors defined in "projection" and
    # determine the range of the first and second components
    xRange = [None, None]
    yRange = [None, None]
    projectedResults = []
    for dp in scaleResults:
        v = dp[1]
        newv = [sum([v[d]*v1[d] for d in range(dim)]), \
               sum([v[d]*v2[d] for d in range(dim)])]
        projectedResults.append((dp[0], newv))
        if xRange[0] is None: xRange[0] = newv[0]
        if xRange[1] is None: xRange[1] = newv[0]
        if yRange[0] is None: yRange[0] = newv[1]
        if yRange[1] is None: yRange[1] = newv[1]
        if newv[0] < xRange[0]: xRange[0] = newv[0]
        if newv[0] > xRange[1]: xRange[1] = newv[0]
        if newv[1] < yRange[0]: yRange[0] = newv[1]
        if newv[1] > yRange[1]: yRange[1] = newv[1]

    img = Image.new('RGB',(width,height), (255,255,255))
    draw = ImageDraw.Draw(img)

    for dp in projectedResults:
        x = (dp[1][0]-xRange[0])*width/(xRange[1]-xRange[0])
        y = (dp[1][1]-yRange[0])*height/(yRange[1]-yRange[0])
        draw.text((x*(1-2*relativeMargin) + width*relativeMargin,\
                   y*(1-2*relativeMargin) + height*relativeMargin), dp[0], (0,0,0))
    img.save(jpeg,'JPEG')
