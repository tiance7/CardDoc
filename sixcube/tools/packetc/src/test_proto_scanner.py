#!/usr/bin/python
# -*- coding: gbk -*-

import unittest
from proto_scanner import *

class ScannerTest(unittest.TestCase):
    def setUp(self):
        self.lex = BuildScanner('proto')
    def doTestHelper(self, text):
        self.lex.NewText(text)
        tokenDict = {}
        self.lex.Scan()
        while self.lex.token != '\0':
            if tokenDict.has_key(self.lex.token):
                tokenDict[self.lex.token] += 1
            else:
                tokenDict[self.lex.token] = 1
            self.lex.Scan()
        return tokenDict

    def testImport(self):
        tokenDict = self.doTestHelper("import abc; import cde;")
        self.assertEqual(tokenDict['import'], 2)
        self.assertEqual(tokenDict[';'], 2)
        self.assertEqual(tokenDict['identifier'], 2)
        
        
    def testComment(self):
        tokenDict = self.doTestHelper('//This Is a comment\n    /* annother comment \n\n\n*/')        
        number_of_comment = tokenDict['comment']
        self.assertEqual(number_of_comment, 2)
        
    def testKeywords(self):
        tokenDict = self.doTestHelper('message { } enum {} enum {}')        
        self.assertEqual(tokenDict['message'], 1);
        self.assertEqual(tokenDict['enum'], 2);
        self.assertEqual(tokenDict['{'], 3);
        self.assertEqual(tokenDict['}'], 3);
    
    def testUndo(self):
        lex = BuildScanner('cpp')
        lex.NewText('int Get(int a, int b, int c) {} ')
        t1, v1 = lex.Scan().ToList()
        t2, v2 = lex.Scan().ToList()
        lex.Undo(2)
        rt1, rv1 = lex.Scan().ToList()
        self.assertEqual(t1, rt1)
        self.assertEqual(v1, rv1)

    def testCppTemplate(self):
        lex = BuildScanner('cpp')
        lex.NewText('std::vector<ACT> actList;')
        token, value = lex.Scan().ToList()
        token_list = [(token, value)]
        while token != '\0':
            token, value = lex.Scan().ToList()
            token_list.append((token, value))
        self.assertEquals(token_list[0], ('identifier', 'std'))
        self.assertEquals(token_list[1], ('::', ''))
        self.assertEquals(token_list[2], ('identifier', 'vector'))
        self.assertEquals(token_list[3], ('<', ''))
        self.assertEquals(token_list[4], ('identifier', 'ACT'))
        self.assertEquals(token_list[5], ('>', ''))
        self.assertEquals(token_list[6], ('identifier', 'actList'))

