"""
@ FIO Parser - stat.py
@ Author cqf
@ Date 2015/10/26

Module for calculating out the statistics from middleFiles.
"""

import logging
import os
import re
import utils
import myconf
import string


# Fields need to be parsed
FIELDS = ["iops", "clat_avg", "lat_avg", "bandwidth"]
PARSE_TYPE = {'pure_r':'_PURE_R','pure_w':'_PURE_W','mix':'_MIX_ALL'}



class Statis(object):
    """calculating out the statistics."""

    def __init__(self):
        pass

    def get_statistic(self,file_path):
        """Get statistic from the csv file_path given.
        Most important parsing fio-log logic.
        1.cuting lines
        2.parsing string into several string blocks
        3.puting string blocks into a dic blocks
        4.generating LogFile object with its arributes
        5.return LogFile object
        """

        raw_lines = utils.cut_file(file_path)

        lines = []
        for l in raw_lines:
            if '\n' != l and '' != l and None != l:
                lines.append(l.replace("\r",""))

        parse_type = utils.get_parse_type(file_path)
        blocks_str = self.split_file(lines,parse_type)

        file_stat = {}
        for block_name, blockData_list in blocks_str.items():
            if None == blockData_list:
                continue
            dic = {}
            num = {}
            for item in blockData_list:
                line_list = item.split(",")
                match = re.search("(.*)/vm", line_list[0])
                if match:
                    group = match.group(1)
                    num[group] = 0;
                    dic[group] = [0.0]*(len(line_list)-1)

            for item in blockData_list:
                line_list = item.split(",")
                match = re.search("(.*)/vm", line_list[0])
                if match:
                    group = match.group(1)
                    num[group] += 1;
                for i in range(1,len(line_list)):
                    dic[group][i-1] += round(string.atof(line_list[i]), 2)                 

            if 'read_block_str' == block_name or 'write_block_str' == block_name:
                for group_name ,group_data_list in dic.items():
                    group_data_list[2] = round(group_data_list[2] / num[group_name],2)

                    group_data_list[3] = round(group_data_list[3] / num[group_name],2)

                    group_data_list[4] = round(group_data_list[4] / num[group_name],2)
                    #print ("######",round(group_data_list[4] / num[group_name],2))

            file_stat[block_name] = dic

        return file_stat



    def split_file(self, lines, parse_type):
        """Split the file."""
        read_line = 0
        write_line = 0
        latence_line = 0
        ioDistrbution_line = 0

        file_blocks_str = {}
        for index in range(len(lines)):
            if self._is_read(lines[index]):
                read_line = index
                continue

            if self._is_write(lines[index]):
                write_line = index
                continue

            if self._is_latence(lines[index]):
                latence_line = index
                continue


            if self._is_ioDistrbution(lines[index]):
                ioDistrbution_line = index
                break


        
        if myconf.PARSE_TYPE["mix"] == parse_type :
            read_block_str = lines[read_line + 1:write_line]
            write_block_str = lines[write_line + 1:latence_line]
        else:
            if myconf.PARSE_TYPE["pure_w"] == parse_type:
                read_block_str = None
                write_block_str = lines[write_line + 1:latence_line]
            else:
                write_block_str = None
                read_block_str = lines[read_line + 1:write_line]

        ioDistrbution_block_str = lines[ioDistrbution_line + 1:]

        logging.debug("  PureRead block str is: %s" % read_block_str)
        logging.debug("  PureWrite block str is: %s" % write_block_str)
        logging.debug("  IODistrbution block str is: %s" % ioDistrbution_block_str)

        file_blocks_str["read_block_str"] = read_block_str
        file_blocks_str["write_block_str"] = write_block_str
        file_blocks_str["ioDistrbution_block_str"] = ioDistrbution_block_str

        return file_blocks_str



    def _is_read(self, line):
        """Return true if read start.

        fileName-PureRead,bw(MB/s),iops,ReadLatMax,ReadLatMin,ReadLatAvg
        """
        if re.match(".*PureRead,", line):
            return True

    def _is_write(self, line):
        """Return true if write start.

        fileName-PureWrite,bw(MB/s),iops,WriteLatMax,WriteLatMin,WriteLatAvg
        """
        if re.match(".*PureWrite,", line):
            return True

    def _is_latence(self, line):
        """Return true if lat start.

        fileName-Latence,2us,4us,10us,20us,50us,100us,250us,500us,750us,...
        """
        if re.match(".*Latence,", line):
            return True

    def _is_ioDistrbution(self, line):
        """Return true if ioDistrbution start.

        fileName-ioDistrbution,2us,4us,10us,20us,50us,100us,250us,500us,750us,...
        """
        if re.match(".*ioDistrbution,", line):
            return True



        