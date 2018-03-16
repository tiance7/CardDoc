#!/usr/bin/python
# -*- coding: gbk -*-

import unittest
from proto_parser import *

class ProtoParserTest(unittest.TestCase):
    def testImport(self):
        text = """
        import LoginProtocol;

        /**
         * ������֤Э��汾.
         * 
         * MSG_AUTH_REQUEST_AUTH_LOGIN
         */
        message RequestProtocolVersion {
            enum { THIS_MSG_TYPE = MSG_AUTH_REQUEST_PROTOCOL_VERSION; }
        
            required UINT32 m_auth_ver = 1;    ///< ��֤Э��汾
            required UINT32 m_gate_ver = 2;    ///< ����Э��汾
            required UINT32 m_game_ver = 3;    ///< ��ϷЭ��汾
            required string m_client_ver = 4;    ///< �ͻ��˰汾
            required fstring32 m_charname = 5;
        }
        """
        parser = ProtoParser()
        parser.ParseString(text)
        parser.DumpTree()
        import_node = parser.tree[0]
        self.assertEqual(import_node.token, "import_stmt")
        self.assertEqual(import_node.value, "LoginProtocol")
        
        
        