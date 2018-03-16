#-*- encoding: gbk -*-

from os.path import splitext, basename, isdir, isfile, join
import glob
import sys
import antlr3
import stringtemplate3
from output.protobufLexer import protobufLexer
from output.protobufParser import protobufParser
from output.protobufWalker import protobufWalker

if len(sys.argv) == 1:
    print "usage: metac.py PROTO [OUTPUT]"
    sys.exit()

class Compiler:
    def __init__(self, templateFile):
        self.templateFile = templateFile
        self.templates = stringtemplate3.StringTemplateGroup(
            file=open(self.templateFile, 'r'),
            lexer='default'
            )

    
    def Compile(self, path_to_input):
        char_stream = antlr3.ANTLRFileStream(path_to_input, "gbk")
        lexer = protobufLexer(char_stream)
        tokens = antlr3.CommonTokenStream(lexer)
        parser = protobufParser(tokens)
        p =  parser.prog()
        #print p.tree.toString()
        root = p.tree
        nodes = antlr3.tree.CommonTreeNodeStream(root)
        nodes.setTokenStream(tokens)
        walker = protobufWalker(nodes)
        walker.templateLib = self.templates
        return walker.prog().toString()

    def Include(self, path):
        module = splitext(basename(path))[0]
        t = self.templates.getInstanceOf("include")
        t['module'] = module
        return t.toString()

    def Composite(self, inc, con):
        t = self.templates.getInstanceOf("cpp_header")
        t['include'] = inc
        t['content'] = con
        return t.toString()


# according input return file list
# if a file as input the this file will be return
# if a dir as input all .proto file withiin the directory will be return
def DetermineInput(fileordir):
    if isfile(fileordir):
        return [fileordir]
    elif isdir(fileordir):
        return glob.glob(join(fileordir, "*.proto"))

if __name__ == "__main__":
    template_file = "proto_meta.stg"
    path_to_input = sys.argv[1]
    input_files = DetermineInput(path_to_input)

    c = Compiler(template_file)
    out = ""
    header = ""

    for f in input_files:
        header += c.Include(f)
        out += c.Compile(f)

    output = c.Composite(header, out)
    if len(sys.argv) > 2:        
        open(sys.argv[2], "w+").write(output)
    else:
        print out
    
