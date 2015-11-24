"""
@ FIO Parser - stat.py
@ Author cqf
@ Date 2015/10/26

@ Update 2015/11/23

Module for calculating out the statistics from middleFiles.
Main function are :
    1.get statistics from fioParser-csv
    2.get total-statistics from fio-logParser-csv
    3.get fluctuation-statistics from fio-logParser-csv

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

    def __init__(self,power_code=0):
        if not utils.power_check(power_code):
            print("Sorry ,the power is illegal !")
            self.prohibition = True
        else:
            self.prohibition = False


    def get_statistic(self,file_path):
        """Get statistic from the csv file_path given.

        """

        if self.prohibition == True:
            print("Sorry ,the power is illegal !")
            return 

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


    def get_fluctuation(self,file_path):
        """Get fluctuation-statistic from the csv file_path given.

        """

        if self.prohibition == True:
            print("Sorry ,the power is illegal !")
            return 

        raw_lines = utils.cut_file(file_path)

        lines = []
        for l in raw_lines:
            if '\n' != l and '' != l and None != l:
                lines.append(l.replace("\r",""))

        title_line = []
        avg_line = []
        title_line = lines[0]
        _avg_lines = lines[-5:]
        for item in _avg_lines:
            if 'avg' in item.lower():
                avg_line = item

        avg_list = avg_line.split(",")
        title_list = title_line.split(",")
        new_title = []
        for item in title_list:
            if 'time' in item.lower():
                new_title.append(item)
                continue
            new_title.append(item)
            new_title.append(item+"-ratio")

        file_stat = []
        file_stat.append(new_title)

        data_lines = lines[1:]
        for line in data_lines:
            if 'var' in line.lower():
                continue
            new_line = []
            line_list = line.split(",")
            new_line.append(line_list[0])
            field_num = 1
            for item in line_list[1:]:
                new_line.append(item)
                item_ratio = self.count_ratio(item,avg_list[field_num])
                new_line.append(item_ratio)
                field_num += 1
            file_stat.append(new_line)
            
        #print("DEBUG-file_stat",file_stat)

        return file_stat


    def get_total(self,file_path):
        """Get total-statistic from the csv file_path given.

        """

        if self.prohibition == True:
            print("Sorry ,the power is illegal !")
            return 

        raw_lines = utils.cut_file(file_path)

        lines = []
        for l in raw_lines:
            if '\n' != l and '' != l and None != l:
                lines.append(l.replace("\r",""))

        title_line = []
        title_line = lines[0]
        title_list = title_line.split(",")

        new_title = []
        vm_name_dic = {}
        for item in title_list:
            if 'time' in item.lower():
                new_title.append(item)
            else:
                new_title.append(item)
                match = re.search("(.*)-read",item)
                if match:
                    group = match.group(1)
                    vm_name_dic[group] = group + '-total'
        
        for key in sorted(vm_name_dic.keys()):
            new_title.append(vm_name_dic[key])
        new_title.append("Read-total")
        new_title.append("Write-total")
        vm_num = len(vm_name_dic)

        file_stat = []
        file_stat.append(new_title)

        data_lines = lines[1:]
        for line in data_lines:
            if 'var' in line.lower():
                continue
            new_line = []
            vm_each_total_dic = {}
            line_total = 0
            line_write_total = 0
            line_read_total = 0

            line_list = line.split(",")
            #new_line.append(line_list[0])
            new_line = line_list
            field_num = 1

            for i in range(1,vm_num+1):
                vm_each_total_dic[i] = float(line_list[2*i-1]) + float(line_list[2*i])
            for i in range(1,vm_num*2+1):
                line_total += float(line_list[i])
                if 0 == i % 2:
                    line_write_total += float(line_list[i])
            line_read_total = line_total - line_write_total

            for key in sorted(vm_each_total_dic.keys()):
                new_line.append(vm_each_total_dic[key]) 
            new_line.append(line_read_total)
            new_line.append(line_write_total)

            file_stat.append(new_line)

        return file_stat
        

    def count_ratio(self, target_data, avg_data):
        result = (float(target_data) - float(avg_data))/(1.0*float(avg_data))
        result = 100 * float( '%.4f' % result)
        return str(result)+'%'


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



        