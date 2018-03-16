#!/usr/bin/env python
# coding: utf-8
import sys, types, optparse, os
from persistConsts import *
from inflection import *
import os.path

# import bundled MakoTemplates module
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))

from xml.etree import ElementTree
from mako.runtime import Context
from mako.template import Template

from DaoProcDef import DaoProcDef
from DaoObjectDef import DaoObjectDef
from DaoContainerDef import DaoContainerDef

tools_dir = os.path.dirname(os.path.realpath(__file__))

def generate_persist(define, isProc, template_name, file_name, package, prefix):
    template = Template(filename=template_name)
    output = file(file_name, 'w')
    output.write(
        template.render_unicode(
            CLS_NAME=define.get_classname(),
            OBJECT_TYPE=define.get_object_type(),
            RAW_DATA_TYPE=define.get_raw_type().upper(),
            fields=define.get_fields(),
            joins=define.get_joins(),
            returns=define.get_returns(),
            keys=define.get_primary_fields(),
            UINQUES=define.get_uniques(),
            INDEXES=define.get_indexes(),
            sqlParser=define,
            fRdr=FieldReader(),
            METHOD=GO_2_METHOD,
            PACKAGE=package,
            PREFIX=prefix,
        ).encode('utf-8')
    )

    # print ' ... done.'


def generate_persist_object(file_name, out_dir, with_sql, prefix):
    '''
        生成DaoObject/DaoProxy类型的源代码。
    '''
    f = file(file_name, 'r')
    tree = ElementTree.ElementTree(file=f)
    root = tree.getroot()

    if 'DaoProc' == root.attrib['skeleton'].strip():
        define = DaoProcDef(root)
    else:
        define = DaoObjectDef(root)

    package = os.path.basename(prefix)
    class_name = define.get_classname()

    file_base = os.path.join(out_dir, underscore(class_name))

    print '-- %s ' % file_name
    
    whole_name = "%sDao" % define.get_classname()

    if "DaoProc" == tree.getroot().attrib['skeleton'].strip():
        generate_persist(define, True,
                         os.path.join(tools_dir, "templates/SampleProc_go.mako"),
                         '%s_proc.go' % file_base,
                         package, prefix)
        whole_name = "%sProc" % define.get_classname()
    else:
        generate_persist(define, False,
                         os.path.join(tools_dir, "templates/SampleDao_go.mako"),
                         '%s.go' % file_base,
                         package, prefix)
        if with_sql:
            print '-- %s ' % '%s.sql' % os.path.join(out_dir, define.get_classname())
            generate_persist(define, False,
                             os.path.join(tools_dir, "templates/SampeDAO_sql.mako"),
                             '%s.sql' % file_base,
                             package, prefix)
    
    return [tree.getroot().attrib['object_type'].strip(), package, whole_name]


def generate_persist_container(def_path, file_name, out_dir, prefix):
    """
        生成DaoArray/DaoMap/DaoHashMap容器类的源代码
    """
    print "XX %s ... " % os.path.join(def_path, file_name),
    container = DaoContainerDef(def_path, file_name, prefix)

    module_dir = os.path.join(out_dir, container.get_module_path())
    # if not os.path.exists(module_dir):
    #     os.mkdir(module_dir)

    container.generate_go(out_dir)

    print "done."
    return [container.get_object_type(), container.get_module_path()[:-1], container.get_element_class()]


def generate_persist_file(def_path, file_name, typeIds, out_dir, with_sql, prefix):
    '''
        生成独立的PersistObject对象的持久类代码
    '''
    full_path = os.path.join(def_path, file_name)
    skeleton = SkeletonReader(full_path).get_skeleton()

    if skeleton in ['DaoProxy', 'DaoObject', 'DaoProc']:
        typeId = generate_persist_object(full_path, out_dir, with_sql, prefix)
        typeIds.append(typeId)
    elif skeleton in ['DaoArray', 'DaoMap', 'DaoHashMap']:
        typeId = generate_persist_container(def_path, file_name, out_dir, prefix)
        typeIds.append(typeId)
    else:
        print 'Unknown Skeleton %s !!!!\n' % skeleton


def generate_persist_dir(options):
    typeids = []
    dir_name = options.define
    out_dir = options.output
    with_sql = options.sql
    prefix = options.prefix
    package = os.path.basename(prefix)

    # 遍历目录逐个处理要持久化对象的定义文件
    for def_path, dir_names, file_names in os.walk(dir_name):
        for file_name in file_names:
            if file_name == 'object_id.xml':
                continue
            base, ext = os.path.splitext(file_name)
            if ext == '.xml':
                generate_persist_file(def_path, file_name, typeids, out_dir, with_sql, prefix)

    # typeids中存放了已经生成的持久化对象的类型ID，需要输出为对应的const定义
    # if len(typeids) > 0:
    #     template = Template(filename=os.path.join(tools_dir, "templates/ids_go.mako"))
    #     output = file(os.path.join(out_dir, "ids.go"), 'w')
    #     output.write(template.render_unicode(
    #         typeIds=typeids,
    #         PACKAGE=package,
    #     ).encode('utf-8'))

        # 对于已经生成的持久化对象类型需要注册其工厂类以便持久化处理类使用
        # field_paths = [x[1] for x in typeids]
        # packages = set(field_paths)

        # template = Template(filename=os.path.join(tools_dir, "templates/init_go.mako"))
        # output = file(os.path.join(out_dir, "init.go"), 'w')
        # output.write(template.render_unicode(
        #     pkgs=packages,
        #     typeIds=typeids,
        #     PACKAGE=package
        # ).encode('utf-8'))


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="usage: %prog [options] <file>.xml | <dir> ")
    parser.add_option("-d", "--define", dest="define", action="store",
                      help="defination file or directory", metavar="DEFINE")
    parser.add_option("-o", "--output", action="store", dest="output", default="output",
                      help="output directory")
    parser.add_option("-p", "--prefix", action="store", dest="prefix", default="uninet/persists",
                      help="prefix of the package")
    parser.add_option("-s", "--sql",
                      action="store_true", dest="sql", default=True,
                      help="generate sql at the same time")

    (options, args) = parser.parse_args()

    if options.define is None or "" == options.define:
        print >> sys.stderr, "A file with persist object definition required!"
        parser.print_help()
        sys.exit(1)
    elif os.path.isdir(options.define):
        print >> sys.stdout, "generate directory: ", options.define
        generate_persist_dir(options)
    elif os.path.isfile(options.define):
        print >> sys.stdout, "generate file: ", options.define
        typeIds = []
        def_path, file_name = os.path.split(options.define)
        generate_persist_file(def_path, file_name, typeIds, options.output, options.sql, options.prefix)
    else:
        print >> sys.stderr, "No such template: ", options.define
