import searchengine
from BeautifulSoup import BeautifulSoup
import unittest

class Test(unittest.TestCase):
    """
    Unit tests for searchengine.
    """

    def test_gettextonly_notags(self):
        """Test crawler.gettextonly: a string with no tags"""
        s = "Just a string."
        soup = BeautifulSoup(s)
        c = searchengine.crawler("")
        self.assertEqual(c.gettextonly(soup), s)

    def test_gettextonly_singletag(self):
        """Test crawler.gettextonly: a single html tag"""
        html = "<html>some text</html>"
        soup = BeautifulSoup(html)
        c = searchengine.crawler("")
        self.assertEqual(c.gettextonly(soup), "some text")

    def test_gettextonly_nestedtag(self):
        """Test crawler.gettextonly: nested html tags"""
        html = "<ul><li>list item 1</li><li>list item 2</li></ul>"
        soup = BeautifulSoup(html)
        c = searchengine.crawler("")
        self.assertEqual(c.gettextonly(soup), "list item 1\nlist item 2")

    def test_getentryid_createnew(self):
        """Test crawler.getentryid: default behaviour
        when requesting a nonexistent database entry is to insert."""
        c = searchengine.crawler("test.db")
        idx = c.getentryid("wordlist","word","test")
        self.assertEqual(idx, c.db.execute(
            'select rowid from wordlist where word="test"'
            ).fetchone()[0])

    def test_getentryid_dontcreatenew(self):
        """Test crawler.getentryid: if requested not to
        create a new entry when a matching entry does not exist, then
        idx should be None."""
        c = searchengine.crawler("test.db")
        idx = c.getentryid("wordlist","word","test",createNew = False)
        self.assertTrue(idx is None)

    def test_getentryid_fetch(self):
        """Test crawler.getentryid: If entry exists,
        return its rowid."""
        c = searchengine.crawler("test.db")
        c.db.execute("insert into wordlist(rowid, word) values (10,'test')")
        idx = c.getentryid("wordlist","word","test")
        self.assertEqual(idx, 10)

    def test_isindexed_urlnotpresent(self):
        """Test crawler.isindexed: If url not present in urllist,
        return False."""
        c = searchengine.crawler("test.db")
        self.assertFalse(c.isindexed("http://www.someurl.com"))

    def test_isindexed_urlpresentnowords(self):
        """Test crawler.isindexed: If url is present in urllist, but
        there are no words associated with the url, assume it has been
        indexed incorrectly and return False."""
        c = searchengine.crawler("test.db")
        c.db.execute("insert into urllist (url) values ('http://www.someurl.com')")
        self.assertFalse(c.isindexed("http://www.someurl.com"))

    def test_isindexed_urlpresentwithwords(self):
        """Test crawler.isindexed: If url is present in urllist, and
        there are words in wordlist associated with that url, return True."""
        c = searchengine.crawler("test.db")
        urlid = c.db.execute(
            "insert into urllist (url) values ('http://www.someurl.com')").lastrowid
        wordid = c.db.execute("insert into wordlist (word) values ('test')").lastrowid
        c.db.execute("insert into wordlocation (urlid, wordid, location) values (%d, %d, 1)" % (urlid, wordid))
        self.assertTrue(c.isindexed("http://www.someurl.com"))


    def test_separatewords(self):
        """Test crawler.separatewords(text)."""
        c = searchengine.crawler("")
        self.assertEqual(["the","cat","in","the","hat"],\
                         c.separatewords("The cat in the hat."))

if __name__=="__main__":
    unittest.main()
