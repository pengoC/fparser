"""
@ FIO Parser - utils.py
@ Author cqf
@ Date 2015/7/28

Module for generating and outputing csv files.
"""

import os
import utils
import csv
import logging
import myconf

class OutputHelper(object):
    """Print fio report"""

    def __init__(self):
        """Intialization method."""

        pass

    def get_CSV_contain(self,path,suffix = "txt"):
        """Most important method
        Put all the files in the folder into the correct csv file,
        the path given is the folder files in.
        """

        files_list = []
        self._get_target_files(path,files_list,suffix)
        name_list = self._get_total_parse_type(files_list,suffix)

        CSV_contain = {}
        for name in name_list:
            _list = []
            for ab_file in files_list:
                if name == os.path.basename(ab_file).replace("."+suffix,""):
                    _list.append(ab_file)
            CSV_contain[name] = _list
        return CSV_contain


    def _get_target_files(self,path,files_list,suffix):
        """Get the target files in the folder given by path."""

        if os.path.exists(path):   
            items = os.listdir(path)
            for f in items :
                sub_item = os.path.join(path,f)
                if os.path.isfile(sub_item):
                    if sub_item.endswith("."+suffix):
                        #print(sub_item)
                        files_list.append(sub_item)
                else:
                    self._get_target_files(sub_item,files_list,suffix)


    def _get_total_parse_type(self,absolute_files_list,suffix):
        """Get the total parse type in the folder given by path,
        these type will be used to name the csv files.
        """

        name_list = []
        for path in absolute_files_list:
            name_list.append(os.path.basename(path).replace("."+suffix,""))
        name_list = list(set(name_list))
        return name_list


    def output_batch_CSV(self,logFile_list,CSV_path):
        """Csv files Output."""
        parse_type = utils.get_parse_type(os.path.basename(CSV_path))

        print(os.path.basename(CSV_path),parse_type)
        logging.debug("+ %s" % os.path.basename(CSV_path))
        logging.debug("  %s" % parse_type)

        read_datas = []
        write_datas = []
        lat_datas = []
        ioD_datas = []

        for logObj in logFile_list:
            print("  "+logObj.fileName)
            logging.debug("  - %s" % logObj.fileName)
            if myconf.PARSE_TYPE["mix"] == parse_type:
                read_datas.append(self.get_readField_data(logObj))
                write_datas.append(self.get_writeField_data(logObj))

            if myconf.PARSE_TYPE["pure_r"] == parse_type:
                read_datas.append(self.get_readField_data(logObj))
                write_datas = [""]

            if myconf.PARSE_TYPE["pure_w"] == parse_type:
                write_datas.append(self.get_writeField_data(logObj))
                read_datas = [""]
            lat_datas.append(self.get_latField_data(logObj,myconf.FIELDS_LAT))
            ioD_datas.append(self.get_ioDField_data(logObj,myconf.FIELDS_ioD))

        csvfile = file(CSV_path,'wb')
        writer = csv.writer(csvfile)

        writer.writerow(myconf.FIELDS_READ)
        writer.writerows(read_datas)
        writer.writerow("")
        writer.writerow(myconf.FIELDS_WRITE)
        writer.writerows(write_datas)
        writer.writerow("")
        writer.writerow(myconf.FIELDS_LAT)
        writer.writerows(lat_datas)
        writer.writerow("")
        writer.writerow(myconf.FIELDS_ioD)
        writer.writerows(ioD_datas)

        if None == parse_type:
            print("@csv generated with warn@  " + CSV_path)
            logging.debug("@csv generated with warn@   %s" % CSV_path)
            print("")
        else:
            print("@csv generated successfully@  " + CSV_path)
            logging.debug("@csv generated successfully@   %s" % CSV_path)
            print("")

        csvfile.close()


    def get_readField_data(self,logFileObj):
        read_data = []
        if logFileObj.readBlock:
            read_data.append(logFileObj.fileName)
            read_data.append(logFileObj.readBlock["bandwidth"])
            read_data.append(logFileObj.readBlock["iops"])
            read_data.append(logFileObj.readBlock["lat_max"])
            read_data.append(logFileObj.readBlock["lat_min"])
            read_data.append(logFileObj.readBlock["lat_avg"])
        return tuple(read_data)



    def get_writeField_data(self,logFileObj):
        write_data = []
        write_data.append(logFileObj.fileName)
        if logFileObj.writeBlock:
            write_data.append(logFileObj.writeBlock["bandwidth"])
            write_data.append(logFileObj.writeBlock["iops"])
            write_data.append(logFileObj.writeBlock["lat_max"])
            write_data.append(logFileObj.writeBlock["lat_min"])
            write_data.append(logFileObj.writeBlock["lat_avg"])
        return tuple(write_data)


    def get_latField_data(self,logFileObj,fields):

        lat_data = []
        lat_data.append(logFileObj.fileName)
        for field in fields:
            if field == "fileName":
                continue
            if logFileObj.latPercentBlock:
                for key,value in logFileObj.latPercentBlock.items():
                    if key == field:
                        lat_data.append(str(value)+'%')
        return lat_data


    def get_ioDField_data(self,logFileObj,fields):
        ioD_data = []
        ioD_data.append(logFileObj.fileName)
        for field in fields:
            if field == "fileName":
                continue
            if logFileObj.ioDistributionBlock:
                for key,value in logFileObj.ioDistributionBlock.items():
                    if key == field:
                        ioD_data.append(value)
        return ioD_data