#!/usr/bin/env python
# coding: utf-8
import sys, types, optparse, os
from persistConsts import *
import os.path

# import bundled MakoTemplates module
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'SchemaObject.zip'))

from xml.etree import ElementTree
from mako.runtime import Context
from mako.template import Template

from DaoProcDef import DaoProcDef
from DaoObjectDef import DaoObjectDef
from DaoContainerDef import DaoContainerDef

cur_dir = os.path.dirname(sys.argv[0])


def generate_persist_object(tree, isProc, template_name, file_name, prefix):
    template = Template(filename=template_name)
    root = tree.getroot()

    #print '  |_ generate %s' % file_name,
    if isProc:
        parser = DaoProcDef(root)
    else:
        parser = DaoObjectDef(root)

    output = file(file_name, 'w')
    output.write(
        template.render_unicode(
            CLS_NAME=parser.get_classname(),
            OBJECT_TYPE=parser.get_object_type(),
            RAW_DATA_TYPE=parser.get_raw_type(),
            root=root,
            fields=root.find('fields'),
            joins=parser.get_joins(),
            returns=root.find('returns'),
            keys=parser.get_primary_fields(),
            UINQUES=parser.get_uniques(),
            INDEXES=parser.get_indexes(),
            sqlParser=parser,
            PREFIX=prefix,
            fRdr=FieldReader()
        ).encode('gb2312')
    )

    #print ' ... done.'


def generate_persist_file(file_name, out_dir, prefix):
    '''
        生成DaoObject/DaoProxy类型的源代码。
    '''

    f = file(file_name, 'r')
    tree = ElementTree.ElementTree(file=f)

    module_dir = os.path.join(out_dir, tree.getroot().attrib['module'].strip())

    if not os.path.exists(module_dir):
        os.mkdir(module_dir)

    sqlsdir = os.path.join(out_dir, "./sqls", tree.getroot().attrib['module'].strip())
    if not os.path.exists(sqlsdir):
        os.mkdir(sqlsdir)

    file_base = os.path.join(module_dir, tree.getroot().tag.strip())

    print '-- %s' % file_name

    if "DaoProc" == tree.getroot().attrib['skeleton'].strip():
        generate_persist_object(tree, True, os.path.join(cur_dir, "templates/SampleProc_h.mako"),
                                '%sProc.h' % file_base, prefix)
        generate_persist_object(tree, True, os.path.join(cur_dir, "templates/SampleProc_cpp.mako"),
                                '%sProc.cpp' % file_base, prefix)
    else:
        generate_persist_object(tree, False, os.path.join(cur_dir, "templates/SampleDao_h.mako"), '%sDao.h' % file_base,
                                prefix)
        generate_persist_object(tree, False, os.path.join(cur_dir, "templates/SampleDao_cpp.mako"),
                                '%sDao.cpp' % file_base, prefix)
        generate_persist_object(tree, False, os.path.join(cur_dir, "templates/SampeDAO_sql.mako"),
                                '%s.sql' % os.path.join(sqlsdir, tree.getroot().tag.strip()), prefix)

    return tree.getroot().attrib['object_type'].strip()


def generate_container(dir_path, f_name, out_dir, prefix):
    """
        生成DaoArray/DaoMap/DaoHashMap类的源代码
    """
    file_name = os.path.join(dir_path, f_name)
    print "XX %s ... " % file_name,
    contDef = DaoContainerDef(dir_path, f_name, prefix)

    module_dir = os.path.join(out_dir, contDef.get_module_path())

    if not os.path.exists(module_dir):
        os.mkdir(module_dir)

    contDef.generate_cpp(out_dir)

    print "done."
    return contDef.get_object_type()


def generate_persist_dir(dir_name, out_dir, prefix):
    typeIds = []

    for dir_path, dir_names, file_names in os.walk(dir_name):
        for file_name in file_names:
            base, ext = os.path.splitext(file_name)
            if ext == '.xml' and base != 'object_id':
                full_path = os.path.join(dir_path, file_name)
                skeleton = SkeletonReader(full_path).get_skeleton()

                if skeleton in ['DaoProxy', 'DaoObject', 'DaoProc']:
                    typeId = generate_persist_file(full_path, out_dir, prefix)
                    typeIds.append(typeId)
                elif skeleton in ['DaoArray', 'DaoMap', 'DaoHashMap']:
                    typeId = generate_container(dir_path, file_name, out_dir, prefix)
                    typeIds.append(typeId)
                else:
                    print 'Unknown Skeleton %s %s !!!!\n' % (file_name, skeleton)
                    #
                    # template = Template(filename=os.path.join(cur_dir, "templates/DaoTypes_h.mako"))
                    # output = file("DaoTypes.h", 'w')
                    # output.write(
                    #     template.render_unicode(
                    #         typeIds=typeIds
                    #     ).encode('gb2312')
                    # )


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="usage: %prog [options] <file>.xml | <dir> ")
    parser.add_option("-d", "--define", dest="define", action="store",
                      help="defination file or directory", metavar="DEFINE")
    parser.add_option("-o", "--output", action="store", dest="output", default="output",
                      help="output directory")
    parser.add_option("-p", "--prefix", action="store", dest="prefix", default="entity",
                      help="prefix of the package")
    parser.add_option("-s", "--sql",
                      action="store_true", dest="sql", default=False,
                      help="generate sql at the same time")

    (options, args) = parser.parse_args()

    if options.define is None or "" == options.define:
        print >> sys.stderr, "A file with persist object definition required!"
        parser.print_help()
        sys.exit(1)
    elif os.path.isdir(options.define):
        print >> sys.stdout, "generate directory: ", options.define
        generate_persist_dir(options.define, options.output, options.prefix)
    elif os.path.isfile(options.define):
        print >> sys.stdout, "generate file: ", options.define
        def_path, file_name = os.path.split(options.define)
        skeleton = SkeletonReader(options.define).get_skeleton()
        if skeleton in ['DaoProxy', 'DaoObject', 'DaoProc']:
            generate_persist_file(options.define, options.output, options.prefix)
        elif skeleton in ['DaoArray', 'DaoMap', 'DaoHashMap']:
            generate_container(os.path.dirname(options.define), os.path.basename(options.define), options.output, options.prefix)
        else:
            print >> sys.stderr, "Unknow Skeleton:", skeleton
    else:
        print >> sys.stderr, "No such template: ", options.define