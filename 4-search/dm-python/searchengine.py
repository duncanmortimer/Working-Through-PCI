import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite

ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class crawler:
    def __init__(self, dbname):
        """
        Initialize crawer with the name of the database.
        """
        self.db = sqlite.connect(dbname)

    def __del__(self):
        self.db.close()

    def dbcommit(self):
        # I don't understand why this is given as a separate function.
        # Perhaps because self.db is really a connection to a
        # database?  Do we sometimes need to do additional things
        # before or after committing?
        self.db.commit()

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
        notags = soup.string
        if notags == None:
            c = soup.contents
            result = []
            for tag in c:
                subtext = self.gettextonly(tag)
                result.append(subtext)
            return "\n".join(result)
        else:
            return notags.strip()

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
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    html = urllib2.urlopen(page)
                except:
                    print "Could not open page %s" % page
                    continue
                soup = BeautifulSoup(html)
                self.addtoindex(page, soup)

                links = soup('a', href = re.compile('.+'))
                for link in links:
                    url = urljoin(page, link['href'])
                    url = url.split('#')[0]
                    if re.match('^http://', url) and not self.isindexed(url):
                        newpages.add(url)
                    linkText = self.gettextonly(link)
                    self.addlinkref(page, url, linkText)
                self.dbcommit()
            pages = newpages

    def createindextables(self):
        """
        Create the database tables
        """
        # Note: Each table has a field 'rowid' by default in sqlite,
        # in addition to the named fields.
        self.db.execute('create table urllist(url)')
        self.db.execute('create table wordlist(word)')
        self.db.execute('create table wordlocation(urlid, wordid, location)')
        self.db.execute('create table linkwords(wordid, linkid)')
        self.db.execute('create table link(fromid, toid)')
        # From wikipedia: "an index is a data structure that increases
        # the speed of access for elements in a database, at the cost
        # of slower writes and increased storage space."
        self.db.execute('create index wordidx on wordlist(word)')
        self.db.execute('create index urlidx on urllist(url)')
        self.db.execute('create index wordurlidx on wordlocation(wordid)')
        self.db.execute('create index urltoidx on link(toid)')
        self.db.execute('create index urlfromidx on link(fromid)')

        self.dbcommit()
