#coding=utf-8
import re

import os
import os.path
import glob

import csv

FIELDS_READ = ["bw(MB/s)", "iops", "ReadLatMax", "ReadLatMin","ReadLatAvg"]
FIELDS_WRITE = ["bw(MB/s)", "iops", "WriteLatMax", "WriteLatMin","WriteLatAvg"]
PARSE_TYPE = {'pure_r':'_PURE_R','pure_w':'_PURE_W','mix':'_MIX_ALL'}


class Person:
    def __init__(self,filename,age):
        self.fileName = filename
        self.agee = age
    def printme(self):
        print(self.fileName)
        print(self.agee)
        print("")


def traverse_dir():
    rootdir = "/root/C"
    for parent,dirnames,filenames in os.walk(rootdir):
        for dirname in  dirnames:
            print("parent is:",parent)
            print("dirname is",dirname)

        for filename in filenames:
            print("parent is:",parent)
            print("filename is:",filename)
            print("the full name of the file is:",os.path.join(parent,filename))


def fun(path):
    for fn in glob.glob(path+os.sep+"*"):
        if os.path.isdir(fn):
            fun(fn)
        else:
            print fn

def scandir(startdir, target) :
    os.chdir(startdir)
    for obj in os.listdir(os.curdir) :
        if obj == target :
            print os.getcwd() + os.sep + obj
        if os.path.isdir(obj) :
            scandir(obj, target)
            os.chdir(os.pardir) #!!!


def getFileStr(level):
    return '  '*level+'- '
def getDicStr(level):
    return '  '*level+'+'

def printFile(path,level):
    if os.path.exists(path):   
        files = os.listdir(path)
        for f in files :
            subpath = os.path.join(path,f)
            if os.path.isfile(subpath):
                print(getFileStr(level)+os.path.basename(subpath))
            else:
                leveli=level+1
                print(getDicStr(level)+os.path.basename(subpath))



             
#traverse_dir()
#fun("/root/C")
#printFile("/root/PYTHON/CStor/fork_1",1)

p1 = Person("/root/PYTHON/CStor/fork_1/rawdata/SSD/4P4V/R1/vm62/r-100r0w-8kb.txt",2)
p2 = Person("/root/PYTHON/CStor/fork_1/rawdata/SSD/4P4V/R1/vm61/r-100r0w-8kb.txt",3)
p3 = Person("/root/PYTHON/CStor/fork_1/rawdata/SSD/4P4V/R1/vm64/r-100r0w-8kb.txt",1)

listt = []
listt.append(p1)
listt.append(p2)
listt.append(p3)

print("start")
print(listt)

for l in listt:
    l.printme()

listt.sort(cmp=None, key=lambda x:x.fileName, reverse=False)

for l in listt:
    l.printme()
