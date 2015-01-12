#coding=utf8

##########################################################################
# File Name: file_related.py
# Author: bright
# mail: brighthush at sina dot com
# Created Time: Mon 12 Jan 2015 02:40:07 PM CST
# Description: This file showed how to read directory, read content from 
# file and write file into file.
##########################################################################

import os

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


def readAndWrite(pathList, des='./des/'):
    try:
        os.stat(des)
    except:
        os.mkdir(des)
    for path in pathList:
        print 'processing %s...' %(path)
        content = readContent(path)
        content = processContent(content)
        items = path.split('/')
        desPath = des + items[-2] + '_' + items[-1]
        print desPath
        if os.path.exists(desPath):
            print 'file name ' + desPath + ' has been used.'
        writeContent(content, desPath)


if __name__ == '__main__':
    print 'Hello World.'
    #fileList = readDir('./sample')
    #readAndWrite(fileList)
