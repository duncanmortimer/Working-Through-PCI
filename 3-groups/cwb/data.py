from collections import defaultdict

def get_data(filename):
    counts = {}
    matrix = map(lambda l: l.split('\t'), file(filename).readlines())
    cols = matrix.pop(0)
    def conv(x):
        try:
            return int(x)
        except ValueError:
            return x
    list_of_numbers = map(lambda x: map(conv, x), matrix)
    list_of_dicts = map(lambda x: dict(zip(cols,x)), list_of_numbers)
    return list_of_dicts
