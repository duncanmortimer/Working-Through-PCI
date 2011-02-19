import feedparser as fp
import re

class URLError(Exception):
    """Exception raised for URLs that don't contain valid feeds."""
    pass

class URLNotFoundError(URLError):
    """Exception raised when the feed resource cannot be located.

    Attributes:
        url -- the URL on which the exception was raised.
    """
    def __init__(self, url):
        self.url = url
    def __str__(self):
        return repr("404 Error: " + self.url +" not found")

class URLRedirectError(URLError):
    """Feed has been moved to a different URL.

    Attributes:
        url -- the URL on which the exception was raised.
        href -- the location we're being redirected to.
    """
    def __init__(self, url, href, status):
        self.url = url
        self.href = href
        self.status = status
    def __str__(self):
        return repr(str(self.status) + " Error: " + self.url +" redirects to " + self.href)

def getWordCounts(url):
    """
    Given the URL of an RSS or Atom feed, extract each word appearing
    in the title or summary field of each post, and construct a
    dictionary with those words as keys, and the total number of times
    each word appears as the entry.  Return a tuple containing the
    title of the feed, and the word count dictionary.
    """
    feedData = fp.parse(url)
    if feedData['status'] == 404: raise URLNotFoundError(url)
    if feedData['status'] == 301 or feedData['status'] == 302:
        raise URLRedirectError(url, feedData['href'], feedData['status'])
    wordCounts = {}

    for entry in feedData['entries']:
        if 'summary' in entry: content = entry['summary']
        else: content = entry['description']
        rawWords = getWords(entry['title'] + ' ' + content)
        for word in rawWords:
            wordCounts.setdefault(word,0)
            wordCounts[word] += 1

    return feedData['feed']['title'], wordCounts

def getWords(theHTML):
    """
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

def processFeedFile(feedFile):
    """processFeedFile(FEEDFILE) -> (WORDCOUNTS, CONTAINWORDCOUNT)

    Takes a relative file path FEEDFILE, each line of which contains
    the URL for an Atom or RSS feed.  Returns a tuple of dictionaries.
    The keys in 'WORDCOUNTS' are the titles of each feed in FEEDFILE,
    and the values are the results obtained by running getWordCounts
    on the feed URL.  The keys in CONTAINWORDCOUNT are the unique
    words obtained from all the feeds, and the values are the number
    of feeds that contain the associated word.
    """

    wordCounts = {}
    containWordCount = {}

    feeds = file(feedFile).readlines()
    numFeeds = len(feeds)

    for feedIndex in range(0,numFeeds):
        print "processing: "+ str(feedIndex + 1) +" of " + str(numFeeds) + " feeds."
        url = feeds[feedIndex].strip()
        try:
            title, wc = getWordCounts(url)
            wordCounts[title] = wc
            for word, count in wc.items():
                containWordCount.setdefault(word, 0)
                containWordCount[word] += 1
        except URLNotFoundError as err:
            print err
        except URLRedirectError as err:
            print err

    return wordCounts, containWordCount

def filterWords(wordCounts, containWordCount, minFrac = 0.1, maxFrac = 0.5):
    """WORDLIST = filterWords(WORDCOUNTS, CONTAINWORDCOUNT, MINFRAC = 0.1, MAXFRAC = 0.5)

    Extract the words from CONTAINWORDCOUNT that appear in less than
    MINFRAC and greater than MAXFRAC fraction of blogs, and return as
    a list.

    (TODO: We pass WORDCOUNTS as an argument so that we know how many
    blogs there are in total; must be a more idiomatic / sensible way
    to do this... perhaps by creating an object to store information
    obtained from a feed list?)
    """

    wordList = []
    numBlogs = float(len(wordCounts))
    for word, count in containWordCount.items():
        frac = float(count)/numBlogs
        if frac>minFrac and frac<maxFrac: wordList.append(word)

    return wordList