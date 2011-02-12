# A dictionary of movie critics and their ratings of a small set of
# movies
from math import sqrt
from collections import defaultdict

critics = {
    'Claudia Puig': {'Just My Luck': 3.0,
                  'Snakes on a Plane': 3.5,
                  'Superman Returns': 4.0,
                  'The Night Listener': 4.5,
                  'You, Me and Dupree': 2.5},
    'Gene Seymour': {'Just My Luck': 1.5,
                  'Lady in the Water': 3.0,
                  'Snakes on a Plane': 3.5,
                  'Superman Returns': 5.0,
                  'The Night Listener': 3.0,
                  'You, Me and Dupree': 3.5},
    'Jack Matthews': {'Lady in the Water': 3.0,
                   'Snakes on a Plane': 4.0,
                   'Superman Returns': 5.0,
                   'The Night Listener': 3.0,
                   'You, Me and Dupree': 3.5},
    'Lisa Rose': {'Just My Luck': 3.0,
               'Lady in the Water': 2.5,
               'Snakes on a Plane': 3.5,
               'Superman Returns': 3.5,
               'The Night Listener': 3.0,
               'You, Me and Dupree': 2.5},
    'Michael Phillips': {'Lady in the Water': 2.5,
                      'Snakes on a Plane': 3.0,
                      'Superman Returns': 3.5,
                      'The Night Listener': 4.0},
    'Mick LaSalle': {'Just My Luck': 2.0,
                  'Lady in the Water': 3.0,
                  'Snakes on a Plane': 4.0,
                  'Superman Returns': 3.0,
                  'The Night Listener': 3.0,
                  'You, Me and Dupree': 2.0},
    'Toby': {'Snakes on a Plane': 4.5,
             'Superman Returns': 4.0,
             'You, Me and Dupree': 1.0}}

def sim_euclidean(prefs, person1, person2):
    prefs1 = prefs.get(person1, {})
    prefs2 = prefs.get(person2, {})
    common_items = set(prefs1.keys()).intersection(set(prefs2.keys()))
    if common_items:
        squares = [pow(prefs1[item]-prefs2[item],2) for item in common_items]
        return 1/(1+sqrt(sum(squares))) # Note: book forgets the sqrt
    else:
        return 0

def sim_pearson(prefs, person1, person2):
    prefs1 = prefs.get(person1, {})
    prefs2 = prefs.get(person2, {})
    common_items = set(prefs1.keys()).intersection(set(prefs2.keys()))

    n = float(len(common_items))
    if n == 0: return 0

    sum1 = sum(prefs1[item] for item in common_items)
    sum2 = sum(prefs2[item] for item in common_items)

    sum1sq = sum(pow(prefs1[item],2) for item in common_items)
    sum2sq = sum(pow(prefs2[item],2) for item in common_items)

    sum12 = sum(prefs1[item]*prefs2[item] for item in common_items)

    denominator = sqrt( (sum1sq - sum1*sum1/n)*(sum2sq - sum2*sum2/n) )
    if denominator:
        return (sum12 - sum1*sum2/n) / denominator
    else:
        return 0

def top_matches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, other, person), other)
              for other in prefs if other != person]
    scores.sort(reverse=True)
    return scores[:n]

def recommend(prefs, person, similarity=sim_pearson):
    scores = defaultdict(list)

    for other in prefs:
        if other == person: continue
        sim = similarity(prefs, person, other)
        for film in prefs[other]:
            scores[film].append((sim, prefs[other][film]))

    recommendations = []
    for film in scores:
        if film in prefs[person]: continue
        sim_sum = sum(sim for (sim, _) in scores[film] if sim > 0)
        score_sum = sum(sim*score for (sim, score) in scores[film] if sim > 0)
        if sim_sum:
            recommendations.append((score_sum/sim_sum, film))

    recommendations.sort(reverse=True)
    print recommendations

def transpose(prefs):
    t = defaultdict(dict)
    for person in prefs:
        for film in prefs[person]:
            t[film][person] = prefs[person][film]
    return t
