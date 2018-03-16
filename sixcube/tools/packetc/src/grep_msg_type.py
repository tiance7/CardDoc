#!/usr/bin/python

import glob
import re

def PrintElem(matches):
    i = 0
    for l in matches:
        print i, l
        i+=1

def IsInclude(matches, text):
    for m in matches:
        if text in m:
            return True

    return False


def GrepFile(filename):
    basere = re.compile("PacketBase\(MSG[a-zA-Z0-9 _]+,")
    #regexp = re.compile("[\ta-zA-Z_0-9 *\]\[/=,]+\)\W*:.*PacketBase\(MSG[a-zA-Z0-9 _]+,")
    regexp = re.compile("::(\w+)\([a-zA-Z0-9<>.&:_ *=,/\"\r\n\t\]\[]+\)\W+:[\r \n\t]*PacketBase\((MSG[a-zA-Z0-9 _]+),")
    text = file(filename).read()
    
    oldmatches = basere.findall(text)
    matches =  regexp.findall(text)

    if  len(oldmatches) != len(matches):
        print filename
        for l in oldmatches:
            if not IsInclude(matches, l):
                print "miss: ", l
        PrintElem(oldmatches)
        PrintElem(matches)
    
    return matches
    
def SaveMatches(matches, filename):
    file = open(filename, "w+")
    for match in matches:
        file.write("%s %s\n" % (match[0], match[1]))

def LoadMatches(filename):
    lines = file(filename).readlines()
    matches = []
    for line in lines:
        matches.append(line[:-1].split(' '))
    return matches

def LoadMatchesDict(filename):
    lines = file(filename).readlines()
    matches = {}
    for line in lines:
        name, index = line[:-1].split(' ')
        matches[name]=index
    return matches

def Test():
    all_matches = []
    for f in glob.glob("..\\..\\..\\protocol\\*.cpp"):
        all_matches += GrepFile(f)
    print ";total %d message type\n" % len(all_matches)    
    SaveMatches(all_matches, "msg2type.txt")
    new_matches = LoadMatches("msg2type.txt")
    new_matches == all_matches
    matchDist = LoadMatchesDict("msg2type.txt")
    # print matchDist
    # print all_matches
    # print new_matches

if __name__ == "__main__":
    Test()
