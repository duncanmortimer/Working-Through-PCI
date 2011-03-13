import searchengine
from BeautifulSoup import BeautifulSoup
import unittest

class TestCrawler(unittest.TestCase):
    """
    Unit tests for searchengine.crawler
    """

    def setUp(self):
        self.c = searchengine.crawler("test.db")

    def tearDown(self):
        del(self.c)

    def test_gettextonly_notags(self):
        """Test crawler.gettextonly: a string with no tags"""
        s = "Just a string."
        soup = BeautifulSoup(s)
        self.assertEqual(self.c.gettextonly(soup), s)

    def test_gettextonly_singletag(self):
        """Test crawler.gettextonly: a single html tag"""
        html = "<html>some text</html>"
        soup = BeautifulSoup(html)
        self.assertEqual(self.c.gettextonly(soup), "some text")

    def test_gettextonly_nestedtag(self):
        """Test crawler.gettextonly: nested html tags"""
        html = "<ul><li>list item 1</li><li>list item 2</li></ul>"
        soup = BeautifulSoup(html)
        self.assertEqual(self.c.gettextonly(soup), "list item 1\nlist item 2")

    def test_getentryid_createnew(self):
        """Test crawler.getentryid: default behaviour
        when requesting a nonexistent database entry is to insert."""
        idx = self.c.getentryid("wordlist","word","test")
        self.assertEqual(idx, self.c.db.execute(
            "SELECT rowid FROM wordlist WHERE word='test'"
            ).fetchone()[0])

    def test_getentryid_dontcreatenew(self):
        """Test crawler.getentryid: if requested not to
        create a new entry when a matching entry does not exist, then
        idx should be None."""
        idx = self.c.getentryid("wordlist","word","test",createNew = False)
        self.assertTrue(idx is None)

    def test_getentryid_fetch(self):
        """Test crawler.getentryid: If entry exists,
        return its rowid."""
        self.c.db.execute("INSERT INTO wordlist(rowid, word) VALUES (10,'test')")
        idx = self.c.getentryid("wordlist","word","test")
        self.assertEqual(idx, 10)

    def test_isindexed_urlnotpresent(self):
        """Test crawler.isindexed: If url not present in urllist,
        return False."""
        self.assertFalse(self.c.isindexed("http://www.someurl.com"))

    def test_isindexed_urlpresentnowords(self):
        """Test crawler.isindexed: If url is present in urllist, but
        there are no words associated with the url, assume it has been
        indexed incorrectly and return False."""
        self.c.db.execute("INSERT INTO urllist (url) VALUES ('http://www.someurl.com')")
        self.assertFalse(self.c.isindexed("http://www.someurl.com"))

    def test_isindexed_urlpresentwithwords(self):
        """Test crawler.isindexed: If url is present in urllist, and
        there are words in wordlist associated with that url, return True."""
        urlid = self.c.db.execute(
            "INSERT INTO urllist (url) VALUES ('http://www.someurl.com')").lastrowid
        wordid = self.c.db.execute("INSERT INTO wordlist (word) VALUES ('test')").lastrowid
        self.c.db.execute("INSERT INTO wordlocation (urlid, wordid, location) VALUES (%d, %d, 1)" % (urlid, wordid))
        self.assertTrue(self.c.isindexed("http://www.someurl.com"))


    def test_separatewords(self):
        """Test crawler.separatewords(text)."""
        self.assertEqual(["the","cat","in","the","hat"],\
                         self.c.separatewords("The cat in the hat."))

class TestSearcher(unittest.TestCase):
    """
    Unit tests for searchengine.searcher
    """

    def setUp(self):
        self.s = searchengine.searcher("test.db")

    def tearDown(self):
        del(self.s)


if __name__=="__main__":
    unittest.main()
