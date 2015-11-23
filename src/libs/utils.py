"""
@ FIO Parser - utils.py
@ Author cqf
@ Date 2015/7/28

Module for all common methods.
"""

import re
import logging
import string
import operator
import os,sys
import myconf
import time

def log_init(debug = False):
    """Set up global logs."""

    log_format = "%(asctime)s %(process)s %(levelname)s [-] %(message)s"
    log_filename = myconf.LOG_FILE_PATH + "parser_" + time.strftime('%Y%m%d%H%I%M%S',time.localtime(time.time())) + ".log"
    log_filemode = 'w'
    log_datefmt='%a, %d %b %Y %H:%M:%S'
    
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(format = log_format, level = log_level, datafmt = log_datefmt, filename = log_filename,filemode = log_filemode)


def get_parse_type(fileString):
    """Get parse type from filename."""
    
    match = re.search("-(\d+)r(\d+)w-",fileString)
    if match:
        rPer = match.group(1)
        wPer = match.group(2)
        if string.atof(rPer) * string.atof(wPer):
        	return myconf.PARSE_TYPE["mix"]
        elif rPer == '0':
        	return myconf.PARSE_TYPE["pure_w"]
        elif wPer == '0':
        	return myconf.PARSE_TYPE["pure_r"]
    else:
        return None

def sort_by_ObjAttr(seq,attr):
    """Sort the sequence container by the attribute."""
    intermed=[(getattr(x,attr),i,x) for i,x in enumerate(seq)]  
    intermed.sort()  
    return [x[-1] for x in intermed]


def cut_file(filePath): 
    """Cut file into lines."""
    if not os.path.isfile(filePath):
        print "Error : file %s do not exsit !!!" % filePath
        return None
    with open(filePath) as f:
        lines = f.read().split("\n")
        return lines

def power_check(code):
    if not code:
        return False
    import hashlib   
    md = hashlib.md5()   
    md.update(code)
    md2 = hashlib.md5()
    md2.update(md.hexdigest())      
    if 'c552c2ee96cfc74ad67bfefbd547031d' == md2.hexdigest():
        return True
    return False