import searchengine
import unittest

class Test(unittest.TestCase):
    """
    Unit tests for searchengine.
    """

    def test_separatewords(self):
        """Test searchengine crawler.separatewords(text)."""
        theCrawler = searchengine.crawler("")
        self.assertEqual(["the","cat","in","the","hat"],\
                         theCrawler.separatewords("The cat in the hat."))

if __name__=="__main__":
    unittest.main()
