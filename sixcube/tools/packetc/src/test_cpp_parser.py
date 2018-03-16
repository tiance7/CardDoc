#!/usr/bin/python
# -*- coding: gbk -*-

import unittest
from cpp_parser import *

class CppParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = CppParser()
    def testClassMemberData(self):
        text = "\nclass A{public: int i,j; int k, a[10]; UINT32 b[30]; };"
        self.parser.ParseString(text)
        #self.parser.DumpTree()
    
    def testClassMemberFunction(self):
        text = "class A{ A(); A(int i); A(int a, int b) {}; };"
        self.parser.ParseString(text)
        #self.parser.DumpTree()
        
    def testScopeOperator(self):
        text = "class A{ std::string m_str; std::vector<int> m_ia;  };"
        self.parser.ParseString(text)
        #self.parser.DumpTree()
        
    def testEnum(self):
        text = "enum A{ a, b = 0, c = 1, d = b + c };"
        self.parser.ParseString(text)
    
    def testAccessOperator(self):
        text = """class ClusterGameResyncCombatStates : public PacketBase { 
               public: private: };"""
        self.parser.ParseString(text)
        #self.parser.DumpTree()

    def testForwardDeclare(self):
        text = " class A; class B //b\n {};"
        self.parser.ParseString(text)
        
    def testEmbedEnum(self):
        text = " class A { enum B { B_1, B_2};  int b;};"
        self.parser.ParseString(text)
        #self.parser.DumpTree()
    
    def testUnsignedInt(self):
        text = " class A { unsigned  int b;};"
        self.parser.ParseString(text)
        #self.parser.DumpTree()
    
    def testComment(self):
        text = """
        /// This is class A
        class A
        {
        public:
            int a; ///< variable a
            /// variable b
            int b; 
        };
        
        enum B 
        {
            B1, ///< this is enum B1
            B2, ///< this is enum B2
            B3 = 3 ///< this is enum B3
            , 
            B4 ///< this is enum B4
        };
        """
        self.parser.ParseString(text)
        self.parser.DumpTree()
        enum_node = self.parser.tree[2]
        self.assertEqual(len(enum_node.childs), 8)
        self.assertEqual(enum_node[0].token, "enum_field_stmt")
        self.assertEqual(enum_node[1].token, "comment")
        self.assertEqual(enum_node[2].token, "enum_field_stmt")
        self.assertEqual(enum_node[3].token, "comment")
        self.assertEqual(enum_node[4].token, "enum_field_stmt")
        self.assertEqual(enum_node[5].token, "comment")
        self.assertEqual(enum_node[6].token, "enum_field_stmt")
        self.assertEqual(enum_node[7].token, "comment")

from util import DumpDir
if __name__ == "__main__":
    def DumpFile(filename):
        parser = CppParser()
        parser.Parse(file(filename).read())
        parser.DumpTree()
        
    #DumpFile("cpp\\ClusterDataType.h")
    #DumpDir("cpp")
    DumpDir("D:\\src\\trunk\\include\\common\\protocol", DumpFile)
    #DumpFile("D:\\src\\trunk\\include\\common\\protocol\\AuthMessage.h")
    #DumpFile("D:\\src\\trunk\\include\\common\\protocol\\ClusterMessage.h")
