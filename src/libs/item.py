"""
@ FIO Parser - item.py
@ Author cqf
@ Date 2015/7/28

Class LogFile.
"""
import numpy

class LogFile:

	def __init__(self,fileName,parseType,readBlock,writeBlock,latPercent,ioDistribution):
		self.fileName = fileName
		self.readBlock = readBlock
		self.writeBlock = writeBlock
		self.latPercentBlock = latPercent
		self.ioDistributionBlock = ioDistribution
		self.parse_type = parseType
		
	def get_fileName(self):
		print "get_fileName"
		return self.fileName
		
	def get_readBlock(self):
		print "get_readBlock"
		return self.readBlock.raw_content
	  
	def get_writeBlock(self):
		print "get_writeBlock"
		return self.writeBlock.raw_content

	def get_latPercentBlock(self):
		print "get_latPercentBlock"
		return self.latPercentBlock.raw_content

	def get_ioDistributionBlock(self):
		print "get_ioDistributionBlock"
		return self.ioDistributionBlock.raw_content

	def printself(self):
		print(self.fileName,self.parse_type,self.readBlock,self.writeBlock,self.latPercentBlock,self.ioDistributionBlock)


class DataLogFile:

	def __init__(self,fileName,parseType,readBlock,writeBlock):
		self.parse_type = parseType
		self.fileName = fileName
		self.readBlock = readBlock
		self.writeBlock = writeBlock
		self.min_r = -1
		self.max_r = -1
		self.avg_r = -1
		self.var_r = -1
		self.min_w = -1
		self.max_w = -1
		self.avg_w = -1
		self.var_w = -1
	

	def init_statics(self,len):
		"""
		Before calling the get_something function to use statics data, 
		you must ensure calling this init funtion first!
		"""
		r_array = numpy.array(self.readBlock[1:len])
		w_array = numpy.array(self.writeBlock[1:len])
		self.min_r = r_array.min()
		self.max_r = r_array.max()
		self.avg_r = r_array.mean()
		self.var_r = r_array.var()
		self.min_w = w_array.min()
		self.max_w = w_array.max()
		self.avg_w = w_array.mean()
		self.var_w = w_array.var()

	def get_fileName(self):
		return self.fileName
		
	def get_readBlock(self):
		return self.readBlock
	  
	def get_writeBlock(self):
		return self.writeBlock

	def get_min_r(self):
		return self.min_r

	def get_max_r(self):
		return self.max_r

	def get_avg_r(self):
		return self.avg_r

	def get_var_r(self):
		return self.var_r
	
	def get_min_w(self):
		return self.min_w

	def get_max_w(self):
		return self.max_w

	def get_avg_w(self):
		return self.avg_w

	def get_var_w(self):
		return self.var_w