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
    def getentryid(self, table, field, value, createNew = True):
        cur = self.db.execute(
            "SELECT rowid FROM %s WHERE %s = '%s'" % (table, field, value))
        res = cur.fetchone()
        if res is None:
            if createNew:
                cur = self.db.execute("INSERT INTO %s (%s) VALUES ('%s')" % (table, field, value))
                return cur.lastrowid
            else: return None
        else:
            return res[0]


    def addtoindex(self, url, soup):
        """
        Index an individual page.
        """
        if self.isindexed(url): return # this occurs if a url is
                                        # linked to multiple times
                                        # from the page in which it is
                                        # first encountered...

        print 'Indexing %s' % url

        words = self.separatewords(self.gettextonly(soup))

        # Add the url to the database and get its id
        urlid = self.getentryid('urllist', 'url', url)

        # Link each word to the url
        for idx in range(len(words)):
            word = words[idx]
            if word not in ignorewords:
                wordid = self.getentryid('wordlist', 'word', word)
                self.db.execute("INSERT INTO wordlocation(urlid,wordid,location) "+\
                                "VALUES (%d, %d, %d)" % (urlid, wordid, idx))

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
        urlid = self.getentryid("urllist","url",url,createNew = False)
        if urlid is not None:
            # Check that there are words associated with the url
            if self.db.execute(
                "SELECT rowid FROM wordlocation WHERE urlid = %d" % urlid
                ).fetchone() is not None:
                return True
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
        self.db.execute("CREATE TABLE urllist(url)")
        self.db.execute("CREATE TABLE wordlist(word)")
        self.db.execute("CREATE TABLE wordlocation(urlid, wordid, location)")
        self.db.execute("CREATE TABLE linkwords(wordid, linkid)")
        self.db.execute("CREATE TABLE link(fromid, toid)")
        # From wikipedia: "an index is a data structure that increases
        # the speed of access for elements in a database, at the cost
        # of slower writes and increased storage space."
        self.db.execute("CREATE INDEX wordidx ON wordlist(word)")
        self.db.execute("CREATE INDEX urlidx ON urllist(url)")
        self.db.execute("CREATE INDEX wordurlidx ON wordlocation(wordid)")
        self.db.execute("CREATE INDEX urltoidx ON link(toid)")
        self.db.execute("CREATE INDEX urlfromidx ON link(fromid)")

        self.dbcommit()

class searcher:
    def __init__(self,dbname):
        self.db=sqlite.connect(dbname)

    def __del__(self):
        self.db.close()

    def getmatchrows(self,query):
        """Pull out all the urls containing every word in query."""
        # Strings to build the query
        fieldlist='w0.urlid'
        tablelist=''
        clauselist=''
        wordids=[]
        # Split the words by spaces
        words=query.split(' ')
        tablenumber=0
        for word in words:
            # Get the word ID
            wordrow=self.db.execute(
                "select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow!=None:
                wordid=wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist+=','
                    clauselist+=' and '
                    clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
                fieldlist+=',w%d.location' % tablenumber
                tablelist+='wordlocation w%d' % tablenumber
                clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
                tablenumber+=1
        # Create the query from the separate parts
        fullquery='select %s from %s where %s' % (fieldlist,tablelist,clauselist)
        cur=self.db.execute(fullquery)
        rows=[row for row in cur]
        return rows,wordids
