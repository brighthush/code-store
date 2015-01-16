#coding=utf8

##########################################################################
# File Name: file_related.py
# Author: bright
# mail: brighthush at sina dot com
# Created Time: Mon 12 Jan 2015 02:40:07 PM CST
##########################################################################

import os
import random

def readDir(dirPath):
    if not dirPath.endswith('/'):
        dirPath += '/'
    pathList = []
    temp = os.listdir(dirPath)
    for path in temp:
        path = dirPath + path
        if path.endswith('.txt'):
            pathList.append(path)
        elif os.path.isdir(path):
            pathList += readDir(path)
        else:
            print path + ' is not a directory or file endswith .txt'
    return pathList


def readContent(contentPath):
    content = ''
    f = open(contentPath)
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        line = line.decode('gbk', 'ignore')
        content += (line + u'\n')
    f.close()
    return content


def writeContent(content, desPath):
    f = open(desPath, 'w')
    f.write(content.encode('utf8', 'ignore'))
    f.close()


def check(ch):
    if ch == u' ' or ch==u'\n':
        return True
    return False


def processContent(content):
    result = u''
    for i in range(len(content)):
        if i>1 and (not check(content[i-1])) and (not check(content[i])):
            result += (u' ' + content[i])
        else:
            result += content[i]
    return result

def floatEqual(a, b, delta):
    if fabs(a - b) <= delta:
        return True
    else:
        return False

def readAndWrite(pathList, des='./des/'):
    print 'begin to write files to %s' %(des)
    n = len(pathList)
    try:
        os.stat(des)
    except:
        os.mkdir(des)
    
    finished = .0
    prefinished = .0
    for path in pathList:
        #print 'processing %s...' %(path)
        content = readContent(path)
        content = processContent(content)
        items = path.split('/')
        desPath = des + items[-2] + '_' + items[-1]
        #print desPath
        #if os.path.exists(desPath):
        #    print 'file name ' + desPath + ' has been used.'
        writeContent(content, desPath)
        finished += 1
        if (finished / (1.0 * n) - prefinished) >= 0.01:
            print 'finished %lf%%' %(finished / (1.0 * n) * 100.0)
            prefinished = finished / (1.0 * n)

if __name__ == '__main__':
    fileList = readDir('./reduced')
    train_set = []
    validate_set = []
    test_set = []
    for filePath in fileList:
        r = random.random()
        if r < 0.7:
            train_set.append(filePath)
        elif r >= 0.7 and r < 0.85:
            validate_set.append(filePath)
        else:
            test_set.append(filePath)
    print 'train_set size %d, vaildate_set size %d, test_set size %d' \
            %(len(train_set), len(validate_set), len(test_set))
    readAndWrite(train_set, './train_set/')
    readAndWrite(validate_set, './validate_set/')
    readAndWrite(test_set, './test_set/')
    #readAndWrite(fileList)


