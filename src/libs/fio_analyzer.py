"""
@ FIO Parser - fio_analyzer.py
@ Author cqf
@ Date 2015/7/28

Module for Parsing and analysising logFile.
"""

import logging
import os
import re
import utils
import string
from libs.item import LogFile
from libs.item import DataLogFile

# Fields need to be parsed
FIELDS = ["iops", "clat_avg", "lat_avg", "bandwidth"]
PARSE_TYPE = {'pure_r':'_PURE_R','pure_w':'_PURE_W','mix':'_MIX_ALL'}

class FioFactory(object):
    """Parse fio report."""

    def __init__(self):

        pass

    def data_log_file_maker(self,file_path):
        """Most important parsing data-log logic.
        1.cuting lines
        2.tracing the lines in the log
        3.generating the readBlock and writeBlock
        4.generating DataLogFile object with its arributes
        """
        #print(file_path)
        parseType = utils.get_parse_type(file_path)
        lines = utils.cut_file(file_path)

        newlines = []
        for l in lines:
            if '\n' != l and '' != l and None != l:
                newlines.append(l)

        #tailLine = ''
        #i = 0
        #while '' == tailLine:
        #    i -= 1
        #    tailLine = ''.join(lines[i].split())   
        #tailLineItems = tailLine.split(",")
        #num = int(round(int(tailLineItems[0])/5000.0)) + 1
        num = len(newlines) + 1
        readBlock = [0] * num
        writeBlock = [0] * num

        lastIndex_r = 1
        lastIndex_w = 1

        for line in lines:
            line = ''.join(line.split())
            #print("###@ line:%s" % line)
            if '' == line:
                continue
            lineItems = line.split(",")
            index = int(round(int(lineItems[0])/5000.0))
            
            #Ensure the current - last == 1, set the repair to fix
            repair = 500
            if '0' == lineItems[2]:
                while index - lastIndex_r > 1:
                    index = int(round((int(lineItems[0]) - repair)/5000.0))
                    repair += 500
                lastIndex_r = index
                if 0 == readBlock[index]:
                    readBlock[index] = int(lineItems[1])


            if '1' == lineItems[2]:
                while index - lastIndex_w > 1:
                    index = int(round((int(lineItems[0]) - repair)/5000.0))
                    repair += 500
                lastIndex_w = index
                if 0 == writeBlock[index]:
                    writeBlock[index] = int(lineItems[1])

            #if '0' == lineItems[2]:
            #    if 0 == readBlock[index]:
            #        readBlock[index] = int(lineItems[1])
            #elif '1' == lineItems[2]:
            #    if 0 == writeBlock[index]:
            #        writeBlock[index] = int(lineItems[1])

        data_log_file = DataLogFile(file_path,parseType,readBlock,writeBlock)

        return data_log_file


    def log_file_maker(self,file_path):
        """Most important parsing fio-log logic.
        1.cuting lines
        2.parsing string into several string blocks
        3.puting string blocks into a dic blocks
        4.generating LogFile object with its arributes
        5.return LogFile object
        """

        lines = utils.cut_file(file_path)
        blocks_str = self.split_report(lines)
        blocks = self.get_blocks(blocks_str)
        parse_type = utils.get_parse_type(file_path)
        log_file = LogFile(file_path,parse_type,blocks["read"],blocks["write"],blocks["latPercent"],blocks["ioDistribution"])
        return log_file


    def get_blocks(self,blocks_str):
        """Put all the string blocks into a dic blocks."""

        blocks = {}
        if blocks_str["read_block_str"]:
            blocks["read"] = self.parse_RW_block_str(blocks_str["read_block_str"])
        else:
            blocks["read"] = None
        
        if blocks_str["write_block_str"]:
            blocks["write"] = self.parse_RW_block_str(blocks_str["write_block_str"])
        else:
            blocks["write"] = None

        blocks["latPercent"] = self.parse_latP_block_str(blocks_str["lat_block_str"])
        
        blocks["ioDistribution"] = self.parse_ioD_block_str(blocks["latPercent"],blocks["read"],blocks["write"])

        return blocks


    def parse_RW_block_str(self,block_str):
        """Get read/write block and format it."""

        block_data = {
           "bandwidth": self._get_bandwidth("\n".join(block_str)),
           "iops": self._get_iops("\n".join(block_str)),
           "lat_max": self._get_lat_max("\n".join(block_str)),
           "lat_min": self._get_lat_min("\n".join(block_str)),
           "lat_avg": self._get_lat_avg("\n".join(block_str)),
        }
        return block_data


    def parse_latP_block_str(self,report):
        """Get latence string block and format it."""
        lat_percent = {'2us':0, '4us':0, '10us':0, '20us':0, '50us':0, '100us':0, '250us':0, '500us':0, '750us':0,\
        '1000us':0, '2ms':0, '4ms':0, '10ms':0, '20ms':0, '50ms':0, '100ms':0, '250ms':0, '500ms':0, '750ms':0,\
        '1000ms':0, '2000ms':0, '>=2000ms':0}
        report_str = ''.join(report)
        report_str = ''.join(report_str.split())
        lines = report_str.split("lat")
        for line in lines:
            #print("@line:::",line)
            part = line.split(":")
            match = re.findall("(\d+|>=\d+)\=(\d+\.\d+)\%", line)
            if match:
                if "usec" in part[0]:
                    for lat_time, percent in match:
                        #print(part[0]+ "#" +lat_time + "@" + percent)
                        lat_percent[lat_time + "us"] = percent
                elif "msec" in part[0]:
                    for lat_time, percent in match:
                        #print(part[0]+ "#" +lat_time + "@" + percent)
                        lat_percent[lat_time + "ms"] = percent
                else:
                    print("Error : Oh!! the unit of the latPercent is not defined, we just allow usec/msec !",line)
                    logging.debug("Error : Oh!! the unit of the latPercent is not defined, we just allow usec/msec :%s" % line)
        return lat_percent


    def parse_ioD_block_str(self,latPercent_block,read_block,write_block):
        """Get ioDistrbution string block and format it."""
        io_distribution = {}
        if read_block and write_block:
            total_iops = read_block["iops"] + write_block["iops"]
        elif read_block:
            total_iops = read_block["iops"]
        elif write_block:
            total_iops = write_block["iops"]
        else:
            total_iops = 0
        for key, value in latPercent_block.items():
            io_distribution[key] = round(string.atof(value) * total_iops / 100, 2)
        return io_distribution


    def split_report(self, lines):
        """Split fio log and analysis it. lines is an list contains the log."""
        start_line = 0
        read_line = 0
        write_line = 0
        lat_startline = 0
        lat_endline = 0

        fio_blocks_str = {}
        for index in range(len(lines)):
            if self._is_start(lines[index]):
                start_line = index

            if self._is_read(lines[index]):
                read_line = index

            if self._is_write(lines[index]):
                write_line = index

            if self._is_lat_start(lines[index],lat_startline):
                lat_startline = index

            if self._is_lat_end(lines[index]):
                lat_endline = index
                break

        if read_line * write_line:
            read_block_str = lines[read_line:write_line]
            write_block_str = lines[write_line:lat_startline]
        else:
            read_block_str = None if read_line == 0 else lines[read_line:lat_startline]
            write_block_str = None if write_line == 0 else lines[write_line:lat_startline]

        lat_block_str = lines[lat_startline:lat_endline]

        logging.debug("  Read block str is: %s" % read_block_str)
        logging.debug("  Write block str is: %s" % write_block_str)
        logging.debug("  Lat block str is: %s" % lat_block_str)

        fio_blocks_str["read_block_str"] = read_block_str
        fio_blocks_str["write_block_str"] = write_block_str
        fio_blocks_str["lat_block_str"] = lat_block_str

        return fio_blocks_str


    def _is_start(self, line):
        """Return true if log start.

        read4k-rand: (groupid=0, jobs=8): err= 0: pid=34199: Fri Jul 10 17:43:48 2015
        """
        if re.match(".*\:\s*\(groupid", line):
            return True

    def _is_read(self, line):
        """Return true if read start.

        read : io=607680KB, bw=1012.6KB/s, iops=126, runt=600140msec
        """
        if re.match(".*read\s*\:", line):
            return True

    def _is_write(self, line):
        """Return true if write start.

        write: io=201432KB, bw=343697B/s, iops=41, runt=600140msec
        """
        if re.match(".*write\s*\:", line):
            return True

    def _is_lat_start(self, line ,lat_start):
        """Return true if lat start.

        lat (usec) : 10=0.01%, 50=0.01%, 100=0.01%, 250=1.93%, 500=3.25%
        lat (usec) : 750=1.33%, 1000=0.70%
        lat (msec) : 2=11.26%, 4=8.33%, 10=6.69%, 20=26.72%, 50=27.26%
        lat (msec) : 100=6.82%, 250=1.91%, 500=1.31%, 750=1.11%, 1000=0.68%
        lat (msec) : 2000=0.66%, >=2000=0.02%
        cpu          : usr=0.22%, sys=0.78%, ctx=81153, majf=0, minf=9
        """
        if lat_start == 0:
            if re.match(".*lat\s*\((\w+)\)\s*\:\s*\d", line):
                return True
        else:
            return False

    def _is_lat_end(self, line):
        """Return true if lat end.

        lat (usec) : 10=0.01%, 50=0.01%, 100=0.01%, 250=1.93%, 500=3.25%
        lat (usec) : 750=1.33%, 1000=0.70%
        lat (msec) : 2=11.26%, 4=8.33%, 10=6.69%, 20=26.72%, 50=27.26%
        lat (msec) : 100=6.82%, 250=1.91%, 500=1.31%, 750=1.11%, 1000=0.68%
        lat (msec) : 2000=0.66%, >=2000=0.02%
        cpu          : usr=0.22%, sys=0.78%, ctx=81153, majf=0, minf=9
        """
        if re.match(".*cpu", line):
            return True

    def _get_lat_avg(self, report):
        """Get lat average from report.

        lat (usec): min=119, max=2459.8K, avg=56660.89, stdev=164252.25
        """
        match = re.search(".*[^sc]lat\s*\((\w+)\).*avg\=\s*(\d+\.{0,1}\d*)\s*([Kk]?),",report)
        if match:
            unit = match.group(1)
            nuit_val = match.group(3)
            value = float(match.group(2))
            if nuit_val.lower() == 'k':
                value = round(value * 1000,2)
            if unit.lower() == "usec":
                value = round(value / 1000,2)
            return value


    def _get_lat_min(self, report):
        """Get lat min from report.

        lat (usec): min=119, max=2459.8K, avg=56660.89, stdev=164252.25
        """
        match = re.search(".*[^sc]lat\s*\((\w+)\).*min\=\s*(\d+\.{0,1}\d*)\s*([Kk]?),",report)
        if match:
            unit = match.group(1)
            nuit_val = match.group(3)
            value = float(match.group(2))
            if nuit_val.lower() == 'k':
                value = round(value * 1000,2)
            if unit.lower() == "usec":
                value = round(value / 1000,2)
            return value


    def _get_lat_max(self, report):
        """Get lat max from report.

        lat (usec): min=119, max=2459.8K, avg=56660.89, stdev=164252.25
        """
        match = re.search(".*[^sc]lat\s*\((\w+)\).*max\=\s*(\d+\.{0,1}\d*)\s*([Kk]?),",report)
        if match:
            unit = match.group(1)
            nuit_val = match.group(3)
            value = float(match.group(2))
            if nuit_val.lower() == 'k':
                value = round(value * 1000,2)
            if unit.lower() == "usec":
                value = round(value / 1000,2)
            return value


    def _get_name(self, report):
        """Get name from report.

        read4k-rand: (groupid=0, jobs=8): err= 0: pid=34199: Fri Jul 10 17:43:48 2015
        """
        match = re.search("(.*)\:\s*\(groupid", report)
        if match:
            return match.group(1)


    def _get_iops(self, report):
        """Get iops from report.

        read : io=70076KB, bw=1151.8KB/s, iops=283, runt= 60843msec
        """
        match = re.search("iops\=(\d+)", report)
        if match:
            return int(match.group(1))
        return 0


    def _get_bandwidth(self, report):
        """Get bandwidth from report.

        write: io=6500.0KB, bw=665533 B/s, iops=162 , runt= 10001msec
        """
        match = re.search("bw\=\s*(\d+\.{0,1}\d*)\s*(\w+)\/s",report)
        if match:
            bandwidth = float(match.group(1))
            unit = match.group(2)
            if unit.lower() == 'b':
                bandwidth = round(bandwidth / 1024 / 1024, 2)
            elif "kb" in unit.lower():
                bandwidth = round(bandwidth / 1024, 2)
            elif "gb" in unit.lower():
                bandwidth = round(bandwidth * 1024, 2)
            return bandwidth