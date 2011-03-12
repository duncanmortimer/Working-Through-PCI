import searchengine
from BeautifulSoup import BeautifulSoup
import unittest

class Test(unittest.TestCase):
    """
    Unit tests for searchengine.
    """

    def test_gettextonly_notags(self):
        """Test searchengine.crawler.gettextonly(soup): a string with no tags"""
        s = "Just a string."
        soup = BeautifulSoup(s)
        c = searchengine.crawler("")
        self.assertEqual(c.gettextonly(soup), s)

    def test_gettextonly_singletag(self):
        """Test searchengine.crawler.gettextonly(soup): a single html tag"""
        html = "<html>some text</html>"
        soup = BeautifulSoup(html)
        c = searchengine.crawler("")
        self.assertEqual(c.gettextonly(soup), "some text")

    def test_gettextonly_nestedtag(self):
        """Test searchengine.crawler.gettextonly(soup): nested html tags"""
        html = "<ul><li>list item 1</li><li>list item 2</li></ul>"
        soup = BeautifulSoup(html)
        c = searchengine.crawler("")
        self.assertEqual(c.gettextonly(soup), "list item 1\nlist item 2")

    def test_separatewords(self):
        """Test searchengine.crawler.separatewords(text)."""
        c = searchengine.crawler("")
        self.assertEqual(["the","cat","in","the","hat"],\
                         c.separatewords("The cat in the hat."))

if __name__=="__main__":
    unittest.main()
