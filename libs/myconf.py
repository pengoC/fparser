FIELDS_READ = ["fileName-PureRead","bw(MB/s)", "iops", "ReadLatMax", "ReadLatMin","ReadLatAvg"]
FIELDS_WRITE = ["fileName-PureWrite","bw(MB/s)", "iops", "WriteLatMax", "WriteLatMin","WriteLatAvg"]
FIELDS_LAT = ['fileName-Latence','2us','4us','10us','20us','50us','100us','250us','500us','750us',\
'1000us','2ms','4ms','10ms','20ms','50ms','100ms','250ms','500ms','750ms','1000ms',\
'2000ms','>=2000ms']
FIELDS_ioD = ['fileName-ioDistrbution','2us','4us','10us','20us','50us','100us','250us','500us','750us',\
'1000us','2ms','4ms','10ms','20ms','50ms','100ms','250ms','500ms','750ms','1000ms',\
'2000ms','>=2000ms']


PARSE_TYPE = {'pure_r':'_PURE_R','pure_w':'_PURE_W','mix':'_MIX_ALL'}

TARGET_SUFFIX = "txt"