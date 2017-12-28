#coding:utf-8
#author by Failymao

__doc__ == '''
- python实现类似Unix系统下管道符查找。
- 原理
    1.先匹配文件名，将匹配到的文件名所在目录用生成器包裹；
    2.遍历生成器，打开所有匹配到的文件名，再次构建生成器--每一个打开的文本都是一个生成器，再组成一个新的生成器；
    3.利用正则方式，进行进行精确查找，匹配特殊字符（通配符 '|'）;
    4.for循环所有的打开文本的生成器,利用正则进行匹配
    5.输出文件所在行

'''


import os
import fnmatch
import gzip
import bz2
import re

def gen_find(filepat, top): #参数filepat为匹配的特殊字符，top为指定目录
    '''
    - 文件目录查找--生成器函数
           使用os.walk构造一个文件，目录遍历器
       - 每次遍历的对象都是返回的是一个三元组(root,dirs,files)
       - root 所指的是当前正在遍历的这个文件夹的本身的地址
       - dirs 是一个 list ，内容是该文件夹中所有的目录的名字(不包括子目录)
       - files 同样是 list , 内容是该文件夹中所有的文件(不包括子目录)   
    '''
    for path, dirlist, filelist in os.walk(top):        #使用os.walk构造一个文件，目录遍历器
        for name in fnmatch.filter(filelist, filepat):  #使用fnmatch.filter方式过滤匹配到的文件名
            yield os.path.join(path,name)               #通过so.path.join()方法，获取查到文件的路径，并构成一个生成器

def gen_opener(filenames):  
    '''
       一次打开一个文件名序列，生成一个文件对象。进行下一次迭代时，文件立即关闭
    'filenames'为查找到的，对应文件名的所有文件目录（绝对路径）--类型为生所有
        可迭代的对象'
    '''
    for filename in filenames:                          #遍历文件
        if filename.endswith('.gz'):
            f = gzip.open(filename, 'rt')               #打开.gz文件，使用gzip函数，打开压缩文件
        elif filename.endswith('.bz2'):
            f = bz2.open(filename, 'rt')                #打开.bz2文件，使用bz2函数，打开压缩文件
        else:
            f = open(filename, 'rt')                    #正常打开其他文件
        yield f                                         #构成以文件名的生成器 - f
        f.close()                                       #关闭所有打开的文件

def gen_concatenate(iterators):
    '''
    - 
    '''
    for it in iterators:                                #遍历生成器连接成的序列
        yield from it                                   #将 yield 操作代理到父生成器上去，返回生成器 it 所产生的所有值

def gen_grep(pattern, lines):
    '''
    - 以正则表达式的方式进行逐行查找，传递两个参数，正则表达式和所有的行
    '''
    pat = re.compile(pattern)                           #编译正则表达式
    for line in lines:
        if pat.search(line):                            #字符串查找，返回对应行，构成一个生成器
            yield line
            
if  __name__ == '__main__':
    lognames = gen_find('access-log*', 'www')           #第一步，匹配文件名，返回查找到的所有文件名路径构成的生成器
    files = gen_opener(lognames)                        #第二步，for生成器，打开匹配到的所有的文件赋值给f(文本生成器)，将内容存放在生成器上
    lines = gen_concatenate(files)                      #第三步，遍历所有文件文件内容的生成器，读取出所有内容
    pylines = gen_grep('(?!)python', lines)             #第四步，正则匹配，类似（grep管道符）从所有文件中查找匹配的字符
    for line in pylines:                                #第五步， 遍历匹配（生成器），打印出对应的行数
        print (line)