from collections import defaultdict
from pydelicious import get_popular, get_userposts, get_urlposts

# Note: Functions changed from book to mostly avoid mutating passed
# data.

def get_users(tag, count=5):
    users = set([])
    for p1 in get_popular(tag=tag)[0:count]:
        for p2 in get_urlposts(p1['url']):
            users.add(p2['user'])
    return users

def get_ratings_for(users):
    user_ratings = {}
    all_items = set([])

    for user in users:
        user_ratings[user] = {}
        for i in range(3):
            try:
                posts = get_userposts(user)
                break
            except:
                print "Failed user "+user+", retrying in 4 seconds"
                time.sleep(4)
        for post in posts:
            url = post['url']
            user_ratings[user][url] = 1.0
            all_items.add(url)

    # Fill in missing items with 0
    # Is this necessary?
    for ratings in user_ratings.values():
        for item in all_items:
            if item not in ratings:
                # Note: this relies on dictionary mutability
                ratings[item] = 0.0

    return user_ratings
