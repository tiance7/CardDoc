#!/usr/bin/python
# -*- coding: gbk -*-

import unittest
from protoc import *

class CompilerTest(unittest.TestCase):
    def testParseArg(self):
        complier = Compiler()
        options, args = complier.ParseArg(["../proto_out", "--cpp-out=../cc", "--as-out=../"])
        self.assertEqual(args, ["../proto_out"])
        self.assertEqual(options.cpp_out_dir, "../cc")  
        self.assertEqual(options.as_out_dir,  "../")
        options, args = complier.ParseArg(["../proto_out", "--as-out=../"])
    
    def testLoadFiles(self):
        complier = Compiler()
        files = complier.LoadFileList(['../proto_out'])
        self.assertTrue(len(files) > 0)
        files = complier.LoadFileList(['../proto_out/ApexMessage.proto'])
        self.assertTrue(len(files) > 0)
        