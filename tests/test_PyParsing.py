'''
Created on 21.06.2020

@author: wf
'''
import unittest
from pyparsing import Word, alphas, nums, oneOf

class TestPyParsing(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testParsing(self):
        greet = Word(alphas) + "," + Word(alphas) + "!"
        hello = "Hello, World!"
        parseString=greet.parseString(hello)
        self.assertEqual(4,len(parseString))
        print(hello, "->", parseString)
        
    def testProceedingsTitle(self):
        pctitle_example="Proceedings of the 10th Symposium on Underwater and Hyperbaric Physiology. La Jolla, California, USA, July 1-2, 2002."
        pctitle=oneOf("Proceedings")+"of"+"the"+Word(nums)+oneOf("st nd th")+oneOf("Symposium Congress")+"on"
        print(pctitle.parseString(pctitle_example))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()