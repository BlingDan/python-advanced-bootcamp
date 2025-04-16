# 列表推导式
mylist = [str(i) + j for i in range(1, 3) for j in 'ABC']   # ['1A', '1B', '1C', '2A', '2B', '2C']

# 字典转化成列表
mydict = {'key1': 'value1', 'key2': 'value2'} # ['key1:value1', 'key2:value2']
mylist2 = [key + ':' + value for key, value in mydict.items()]

# 推导式生成字典
mydict = {i: i**2 for i in range(1, 10)}


