from os.path import splitext, basename
import sys
import antlr3
import stringtemplate3
from output.protobufLexer import protobufLexer
from output.protobufParser import protobufParser
from output.protobufWalker import protobufWalker

if len(sys.argv) == 1:
    print "usage: test.py STG PROTO"
    sys.exit()

input = '...what you want to feed into the parser...'
#char_stream = antlr3.ANTLRStringStream(input)
# or to parse a file:
#path_to_input = "D:\\dev\\icloud\\trunk\\src\\proto\\defines\\CharMessage.proto"
path_to_input = sys.argv[2]
#path_to_input = "example.proto"
char_stream = antlr3.ANTLRFileStream(path_to_input, "gbk")
# or to parse an opened file or any other file-like object:
# char_stream = antlr3.ANTLRInputStream(file)

lexer = protobufLexer(char_stream)
tokens = antlr3.CommonTokenStream(lexer)
#print tokens
parser = protobufParser(tokens)
p =  parser.prog()
#%print p
#%print type(p.tree)
#print p.tree.toStringTree()


#templateFile = "proto_cpp.stg"
templateFile = sys.argv[1]
templates = stringtemplate3.StringTemplateGroup(
    file=open(templateFile, 'r'),
    lexer='default'
    )
    

root = p.tree
nodes = antlr3.tree.CommonTreeNodeStream(root)
nodes.setTokenStream(tokens)
walker = protobufWalker(nodes)
walker.templateLib = templates
print walker.symbol_table_stack

guard = splitext(basename(path_to_input))[0].upper()

t = templates.getInstanceOf("cpp_header")
t['file_guard_marco'] = '__%s_PB_H__' % guard
t['content'] = walker.prog()
print t.toString().encode("gbk")

