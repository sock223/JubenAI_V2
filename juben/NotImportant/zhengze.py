import re







xs = re.compile(r'([0-9一两三仨二壹四肆]+).*?线索')
print(xs.findall('ad一二啊你不行啊987两三四五12一3线索456a4d三f线索a'))



#\u767e\u5343\u96f6 百千万
print(re.findall(r'([0-9一两三仨二壹四肆]+).*?线索',"ad一二啊你不行啊987两三四五123线索456a4df线索a"))
print(re.findall('线索',"ad一f12234567a4df线索a"))


xs = re.compile(r'\d{6}')
print(xs.findall('ad一二啊你不行啊987两三四五12123212312311一3线索456a4d三f线索a'))

