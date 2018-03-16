#!/usr/bin/python
# -*- coding: gbk -*-

import sys
import glob
import os.path
import time
from optparse import OptionParser

from proto_parser import ProtoParser
from proto_to_cpp import CppGenerator
from proto_to_as import ActionScriptGenerator
from util import RunProfile

class Compiler:
    """
    这是一个实验性质的协议版本解释器。计划读取google protobuf 的协议定义语言然后生成或是xml。
    最后生成c++和actionscript协议类.
    """

    def __init__(self):
        pass

    def ParseArg(self, argv):
        """
        Parse command line option
        Usage:
          protoc [INPUT_FILE|INPUT_DIRECTORY] --cpp-out=[CPP_OUT_DIR] --as-out=[AS_OUT_DIR]          
        """
        parser = OptionParser()
        parser.add_option("-c", "--cpp-out", dest="cpp_out_dir",
            help="write cpp files to the directory", metavar="CPP_OUT_DIR")
        parser.add_option("-a", "--as-out", dest="as_out_dir",
            help="write action script to the directory", metavar="AS_OUT_DIR")

        return parser.parse_args(argv)

    def LoadFileList(self, input_paths):
        """
        Load file list in input_paths list.
        input path can be directory or file.
        """
        files = []
        for path in input_paths:
            if os.path.isdir(path):
                files += glob.glob(os.path.join(path, "*.proto"))
            elif os.path.isfile(path):
                files.append(path)
        return files

    def Compile(self, argv):
        options, args = self.ParseArg(argv)

        # determine files to be compile
        proto_source_files = self.LoadFileList(args)
        if len(proto_source_files) <= 0:
            sys.stderr.write("NO input files.")
            sys.exit(0)

        # setup language generator
        self.generator_list = []
        if hasattr(options, "cpp_out_dir"):
            self.generator_list.append(CppGenerator(options.cpp_out_dir))
        if hasattr(options, "as_out_dir"):
            self.generator_list.append(ActionScriptGenerator(options.as_out_dir))

        for file in proto_source_files:
            self.CompileFile(file)

    def CompileFile(self, filepath):
        parser = ProtoParser()
        for generator in self.generator_list:
            parser.RegisterGenerator(generator)
        parser.ParseFile(filepath)
        for generator in self.generator_list:
            generator.generate(parser.tree, filepath)


def Main():
    print "ProtoC Begin "
    start = time.time()
    compiler = Compiler()
    compiler.Compile(sys.argv[1:])
    print "ProtoC End. (used %f)." % (time.time() - start)

if __name__ == "__main__":
    RunProfile(Main)
