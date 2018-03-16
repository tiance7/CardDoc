#!/usr/bin/python
# -*- coding: gbk -*-
import os
import glob
import string


def IsNum(s):
    """
           字符串S中的字符是否都是数字字符    
    """
    for c in s:
        if c not in string.digits:
            return False
    return True


def DumpDir(dir, func):
    index = 1
    files = glob.glob(dir)
    for file in files:
        print " File \"%s\", line 1, [%d/%d] " % (os.path.abspath(file), index, len(files))
        func(file)
        index += 1
        
def DumpDirExt(file_ext, input_path, target_path, func):
    filelist = []
    if os.path.isfile(input_path):
        filelist.append(input_path)
    elif os.path.isdir(input_path):
        filelist = glob.glob(input_path + "//*" + file_ext)
    assert len(filelist) > 0

    target_dir = target_path
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    for filename in filelist:
        func(filename, target_dir)

def delete_file_folder(target_path):  
    '''delete files and folders''' 
    if os.path.isfile(target_path):
        os.remove(target_path)
    elif os.path.isdir(target_path):  
        for item in os.listdir(target_path):  
            itempath=os.path.join(target_path,item)  
            delete_file_folder(itempath)  
        os.rmdir(target_path)

def DumpDirToGo(file_ext, input_path, target_path, pkg_prefix, type_ids, func):
    filelist = []
    if os.path.isfile(input_path):
        filelist.append(input_path)
    elif os.path.isdir(input_path):
        filelist = glob.glob(input_path + "//*" + file_ext)
    assert len(filelist) > 0

    target_dir = target_path
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
    else:
        for item in os.listdir(target_dir):
            if item == "PersistMessage":
                continue
            
            itempath=os.path.join(target_dir,item)
            if os.path.isdir(itempath):
                delete_file_folder(itempath)

    for filename in filelist:
        func(filename, target_dir, pkg_prefix, type_ids)


def RunProfile(main):
    import hotshot, hotshot.stats, test.pystone

    prof = hotshot.Profile("stones.prof")
    prof.runcall(main)
    prof.close()
    stats = hotshot.stats.load("stones.prof")
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(20)
