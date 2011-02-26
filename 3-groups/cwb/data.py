from collections import defaultdict

def get_data(filename):
    lines = file(filename).readlines()
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for l in lines[1:]:
        ls = l.strip().split('\t')
        rownames.append(ls[0])
        data.append([float(x) for x in ls[1:]])
    return rownames, colnames, data


