import pandas as pd
import random

LOOP = 1000000
MAX = 4000
LENGTH = 10
stat = {}

def generate():
    length = random.randint(1,LENGTH)
    for i in range(length):
        j = random.randint(0, MAX)
        if stat.get(j,None) is not None:
            stat[j]+=1
        else:
            stat[j]=0


for i in range(LOOP):
    generate()

# TODO 完成分布测试
stat_list = []
for key, value in stat.items():
    temp = [key,value]
    stat_list.append(temp)


df = pd.DataFrame(stat_list,columns=['id','count'])

print(df.describe())

"""
 ✗ python test_random_gentext.py
                id        count
count  4001.000000  4001.000000
mean   2000.000000  1374.021995
std    1155.133542    36.568046
min       0.000000  1238.000000
25%    1000.000000  1349.000000
50%    2000.000000  1374.000000
75%    3000.000000  1399.000000
max    4000.000000  1497.000000
"""

"""
模拟测试了一下，4000模拟字的一级字库的模拟，
生成100万个样本，每个样本随机1-10个字，
然后我看分布均匀么？
结果是：
    均值是1374，方差是36，最小的1238，
    最大的1497，还是算均匀的。这下我就放心了。
"""