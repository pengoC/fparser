#!/usr/bin/env python

VER = "FIO Parser 1.2.0"
"""
@ FIO Parser - fparser.py
@ Author cqf
@ Date 2015/7/28

@ Update 2015/9/14
@ Update 2015/10/26
@ Update 2015/11/6
@ Update 2015/11/23

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
from libs.statis import Statis
from libs.output_helper import OutputHelper

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]), os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "lib", "__init__.py")):
    sys.path.insert(0, os.path.join(possible_topdir))


def parse_args(argv):
    """Parses command-line arguments."""

    parser = optparse.OptionParser(version = VER)
    parser.add_option('--singlefile', action = "store",
            dest = "singlefile",
            help = "\n Fio singlefile path")

    parser.add_option('--infolder', action = "store",
            dest = "infolder",
            help = "\n Give the InputFolder and we get the files recursively")

    parser.add_option('--outfolder', action = "store",
            dest = "outfolder",
            help = "\n Set folder for storing the csv files")

    parser.add_option("-l","--log", action = "store_true",
            dest = "datalog", default = False,
            help = "\n Parse the rw-data-log files.")

    parser.add_option("-s","--statistic", action = "store_true",
            dest = "statistic", default = False,
            help = "\n get the statistics from middle-files.")

    parser.add_option("-f","--fluctuation", action = "store_true",
            dest = "fluctuation", default = False,
            help = "\n get the fluctuation from middle-files.")

    parser.add_option("-t","--total", action = "store_true",
            dest = "total", default = False,
            help = "\n get the total from middle-files.")

    parser.add_option("-d", "--debug", action = "store_true",
            dest = "debug", default = False,
            help = "\n Enable debug message.")

    parser.add_option("--power", action = "store",
            dest = "power_code",
            help = "\n Long live the code!")

    (opts, args) = parser.parse_args(argv)
    #print("opts : %s" % opts)
    #print("argv : %s" % argv)

    if None == opts.singlefile and None == opts.infolder:
        print "\n :) Need help ?  Please read the manual: --help or -h\n"
        sys.exit(1)

    if opts.singlefile and False == os.path.isfile(opts.singlefile):
        print "\n ERROR: are you sure this is a file ? : %s" % opts.singlefile
        sys.exit(1)
    if opts.infolder and False == os.path.isdir(opts.infolder):
        print "\n ERROR: are you sure this is a folder ? : %s" % opts.infolder
        sys.exit(1)
    return opts


def folder_parse(folder_path, output_path = '.',suffix = 'txt',workmode = 0,power_code = 0):

    out_helper = OutputHelper()
    CSV_contain = out_helper.get_CSV_contain(folder_path,suffix)
    fio_factory = FioFactory()

    #fio parse mode
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

    #datalog parse mode
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

    #fio statistic mode
    if 2 == workmode:
        statis = Statis(power_code)
        for key, value in CSV_contain.items():
            logging.debug("statistic-CSV-name: %s" % key)
            file_name = value[0]
            file_stat = statis.get_statistic(file_name)
            out_helper.output_statistic_CSV(file_stat,output_path + '/' + key +"-statistics.csv")

    #fio log fluctuation mode
    if 3 == workmode:
        statis = Statis(power_code)
        for key, value in CSV_contain.items():
            logging.debug("fluctuation-statistic-CSV-name: %s" % key)
            file_name = value[0]
            file_stat = statis.get_fluctuation(file_name)
            out_helper.output_normal_CSV(file_stat,output_path + '/' + key +"-fluctuation.csv")

    #fio log total mode
    if 4 == workmode:
        statis = Statis(power_code)
        for key, value in CSV_contain.items():
            file_name = value[0]
            parse_type = utils.get_parse_type(file_name)
            if myconf.PARSE_TYPE["mix"] == parse_type:
                logging.debug("total-statistic-CSV-name: %s" % key)
                file_stat = statis.get_total(file_name)
                out_helper.output_normal_CSV(file_stat,output_path + '/' + key +"-total.csv")


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
    print("job is scheduling ...\n")


    if options.statistic:
        suffix = "csv"
        folder_parse(options.infolder, options.outfolder,suffix,2,options.power_code)
        print("\njob well done ! --- resultPath: %s" % options.outfolder)
        return

    if options.fluctuation:
        suffix = "csv"
        folder_parse(options.infolder, options.outfolder,suffix,3,options.power_code)
        print("\njob well done ! --- resultPath: %s" % options.outfolder)
        return

    if options.total:
        suffix = "csv"
        folder_parse(options.infolder, options.outfolder,suffix,4,options.power_code)
        print("\njob well done ! --- resultPath: %s" % options.outfolder)
        return

    suffix = myconf.TARGET_SUFFIX
    if options.infolder:
        if options.outfolder:
            if options.datalog:
                suffix = myconf.TARGET_DATALOG_SUFFIX
                folder_parse(options.infolder, options.outfolder,suffix,1)
                print("\njob well done ! --- resultPath: %s" % options.outfolder)
                return
            folder_parse(options.infolder, options.outfolder,suffix)
            print("\njob well done ! --- resultPath: %s" % options.outfolder)
        else:
            folder_parse(options.infolder)
            print("\njob well done ! --- resultPath: Current foder")

    if options.singlefile:
        singlefile_parse(options.singlefile)


if __name__ == "__main__":
	main(sys.argv)