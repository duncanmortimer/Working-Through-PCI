import feedparser as fp
import re

def getWordCounts(url):
    """getWordCounts(URL)

    Given the URL of an RSS or Atom feed, extract each word appearing
    in the title or summary field of each post, and construct a
    dictionary with those words as keys, and the total number of times
    each word appears as the entry.
    """
    dat = fp.parse(url)
    wordCounts = {}

    for item in dat['entries']:
        rawWords = getWords(item['title'] + ' ' + item['summary'])
        for word in rawWords:
            wordCounts.setdefault(word,0)
            wordCounts[word] += 1

    return wordCounts

def getWords(theHTML):
    """getWords(THEHTML)

    From a string of html, THEHTML, strip out all the HTML tags, and
    retrieve a list of the words used in the HTML in the order in
    which they appear.
    """

    # Strip out the HTML from the input
    rawText = re.sub("<[^>]*>"," ",theHTML).lower()

    # Strip out any punctuation
    rawText = re.sub("[^a-z]+"," ",rawText).strip()

    # Split the resulting string at the spaces
    wordVec = rawText.split(" ")

    return wordVec
