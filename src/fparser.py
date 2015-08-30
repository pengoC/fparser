#!/usr/bin/env python

VER = "FIO Parser 1.0.0"
"""
@ FIO Parser - fparser.py
@ Author cqf
@ Date 2015/7/28

Implements the CLI API.
For the scenes of pure-read/pure-write and mix-io.
"""

import logging
import optparse
import os
import sys
import re

from libs import utils
from libs import myconf
from libs.item import LogFile
from libs.fio_analyzer import FioFactory
from libs.output_helper import OutputHelper


possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "lib", "__init__.py")):
    sys.path.insert(0, os.path.join(possible_topdir))



def parse_args(argv):
    """Parses command-line arguments."""

    parser = optparse.OptionParser(version = VER)
    parser.add_option('--singlefile', action = "store",
            dest = "singlefile",
            help = "Fio singlefile path")

    parser.add_option('--folder', action = "store",
            dest = "folder",
            help = "Parse fio logs from folder recursively")

    parser.add_option('--outfolder', action = "store",
            dest = "outfolder",
            help = "Set folder for storing the csv files")

    parser.add_option("--log", action = "store_true",
            dest = "datalog", default = False,
            help = "Parse the rw-data-log files.")

    parser.add_option("-d", "--debug", action = "store_true",
            dest = "debug", default = False,
            help = "Enable debug message.")

    (opts, args) = parser.parse_args(argv)
    #print("opts : %s" % opts)
    #print("argv : %s" % argv)

    if None == opts.singlefile and None == opts.folder:
        print "\n:) Need help ?  Please read the manual: --help or -h\n"
        sys.exit(1)

    if opts.singlefile and False == os.path.isfile(opts.singlefile):
        print "ERROR: are you sure this is a file ? : %s" % opts.singlefile
        sys.exit(1)
    if opts.folder and False == os.path.isdir(opts.folder):
        print "ERROR: are you sure this is a folder ? : %s" % opts.folder
        sys.exit(1)
    return opts


def folder_parse(folder_path, output_path = '.',suffix = 'txt',workmode = 0):

    out_helper = OutputHelper()
    CSV_contain = out_helper.get_CSV_contain(folder_path,suffix)
    fio_factory = FioFactory()
    if 0 == workmode:
        CSV_logFileOBJ_contain = {}
        for key, value in CSV_contain.items():
            logging.debug("CSV-name: %s" % key)
            logFile_list = []
            for f_name in value:
                logging.debug("  logFile: %s" % f_name)
                # print(f_name)
                logFileObj = fio_factory.log_file_maker(f_name)
                logFile_list.append(logFileObj)
            logFile_list.sort(cmp = None, key = lambda x:x.fileName, reverse = False)
            CSV_logFileOBJ_contain[key] = logFile_list
        for key,value in CSV_logFileOBJ_contain.items():
            out_helper.output_batch_CSV(value, output_path + '/' + key +".csv")

    if 1 == workmode:
        CSV_dataLogFileOBJ_contain = {}
        for key, value in CSV_contain.items():
            logging.debug("dataLog-CSV-name: %s" % key)
            dataLogFile_list = []
            for f_name in value:
                logging.debug("  dataLogFile: %s" % f_name)
                #print(f_name)
                dataLogFileObj = fio_factory.data_log_file_maker(f_name)
                dataLogFile_list.append(dataLogFileObj)
            dataLogFile_list.sort(cmp = None, key = lambda x:x.fileName, reverse = False)
            CSV_dataLogFileOBJ_contain[key] = dataLogFile_list

        for key,value in CSV_dataLogFileOBJ_contain.items():
            out_helper.output_batch_data_CSV(value, output_path + '/' + key +".csv")




def singlefile_parse(filename):
    fio_factory = FioFactory()
    logFileObj = fio_factory.log_file_maker(filename)
    logFileObj.printself()


def main(argv):
    """Main function to run."""
    
    os.environ["LANG"] = "en_US.UTF8"
    parser = optparse.OptionParser(version = VER)
    options = parse_args(argv)
    utils.log_init(options.debug)

    print("********************************************************************")
    print("job scheduling ...\n")
    suffix = myconf.TARGET_SUFFIX
    if options.folder:
        if options.outfolder:
            if options.datalog:
                suffix = myconf.TARGET_DATALOG_SUFFIX
                folder_parse(options.folder, options.outfolder,suffix,1)
                print("\njob well done ! --- resultPath: %s" % options.outfolder)
                return
            folder_parse(options.folder, options.outfolder,suffix)
            print("\njob well done ! --- resultPath: %s" % options.outfolder)
        else:
            folder_parse(options.folder)
            print("\njob well done ! --- resultPath: Current foder")

    if options.singlefile:
        singlefile_parse(options.singlefile)


if __name__ == "__main__":
	main(sys.argv)