#Import re

class crawler:
    def __init__(self, dbname):
        """
        Initialize crawer with the name of the database.
        """
        pass

    def __del__(self):
        pass

    def dbcommit(self):
        pass

    # Auxiliary functions for getting an entry id and adding it if
    # it's not present
    def getentryid(self, table, field, value, createnew = True):
        return None

    def addtoindex(self, url, soup):
        """
        Index an individual page.
        """
        print 'Indexing %s' % url

    def gettextonly(self, soup):
        """
        Extract the text from an HTML page (no tags)
        """
        return None

    def separatewords(self, text):
        """
        Separate the words by any non-whitespace character, and
        convert to lower case.
        """
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']

    def isindexed(self, url):
        """
        Return True if this url is already indexed
        """
        return False

    def addlinkref(self, urlFrom, urlTo, linkText):
        """
        Add a link between two pages
        """
        pass

    def crawl(self, pages, depth = 2):
        """
        Starting with a list of pages, do a breadth first search to
        the given depth, indexing pages as we go.
        """
        pass

    def createindextables(self):
        """
        Create the database tables
        """
        pass
