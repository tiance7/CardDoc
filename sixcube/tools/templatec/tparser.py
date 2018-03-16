#!/usr/bin/env python
# coding: utf-8
import sys
import optparse
import os
import os.path

from TemplateDefine import *

#import bundled MakoTemplates module
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))

from mako.runtime import Context
from mako.template import Template


def generate_template_dir(dir_name, ouput_dir):
    typeIds = []

    for dir_path, dir_names, file_names in os.walk(dir_name):
        for file_name in file_names:
            base, ext = os.path.splitext(file_name)
            if ext == '.xml':
                full_path = os.path.join(dir_path, file_name)
                generate_template_file(full_path, ouput_dir)


def generate_template_file(file_name, output_dir):
    define = TemplateDefine(file_name)

    skeleton = os.path.join(os.path.dirname(sys.argv[0]), "%sTemplate.mako" % define.get_skeleton())
    if not os.path.exists(skeleton):
        return
        ##print >> sys.stderr, "No Such Skeleton : %s \n" % define.get_skeleton()
        ##sys.exit(1)   //模板表数据未全部添加，暂时先跳过

    print >> sys.stderr, file_name, define.get_class_name()
    template = Template(filename=skeleton)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output = file(os.path.join(output_dir, "%s.go" % define.get_class_name()), 'w')
    output.write(
        template.render_unicode(
            T_NAME = define.get_class_name(),
            xmldef = define,
            fields = define.root
        ).encode('utf-8')
    )


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="usage: %prog [options] <file>.xml | <dir> <output_dir>")

    (options, args) = parser.parse_args()

    if len(args) != 2:
        print >> sys.stderr, "usage: %prog [options] <file>.xml | <dir> <output_dir>!"
    elif os.path.isdir(args[0]):
        generate_template_dir(args[0], args[1])
    elif os.path.exists(args[0]):
        generate_template_file(args[0], args[1])
    else:
        print >> sys.stderr, "define file not existed!"
