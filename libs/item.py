"""
@ FIO Parser - item.py
@ Author cqf
@ Date 2015/7/28

Class LogFile.
"""

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

