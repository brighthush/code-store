#coding=utf-8
"""
@author: Bright
@description: This file to read input data which in the format:
    rowNum colNum
    label feature_1 feature_2 ... feature_colNum
    ...
    label feature_1 feature_2 ... feature_colNum
"""

import numpy
import theano

def getLabel(str):
    str = str.strip()
    items = str.split('/')
    items = items[-1].split('_')
    label = items[0]
    return label

def readData(path='./data.in'):
    labelHash = {}
    labels = []
    rowNames = []
    x = []
    y = []
    fin = open(path, 'r')
    line = fin.readline()
    line = line.strip()
    items = line.split(' ')
    row = int(items[0])
    col = int(items[1])
    while True:
        line = fin.readline()
        if not line:
            break
        line = line.strip()
        
        items = line.split(' ')
        rowName = items[0]
        rowNames.append(rowName)
        label = getLabel(rowName)
        if label not in labelHash:
            labels.append(label)
            labelHash[label] = len(labels) - 1
        
        y.append(labelHash[label])
        xrow = []
        for i in range(1, len(items)):
            xrow.append(float(items[i]))
        x.append(xrow)
    fin.close();
    return x, y, labels, labelHash, rowNames

def generateShared(x, y):
    def shared_data(data_x, data_y, borrow=True):
        x_shared = theano.shared(numpy.asarray(data_x,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        y_shared = theano.shared(numpy.asarray(data_y,
                                               dtype='int32'),
                                 borrow=borrow)
        return (x_shared, y_shared)
    
    x = numpy.array(x)
    y = numpy.array(y)
    n = x.shape[0]
    train_x = x[ : n*7/10 ]
    train_y = y[ : n*7/10 ]
    validate_x = x[ n*7/10 : n*85/100 ]
    validate_y = y[ n*7/10 : n*85/100 ]
    test_x = x[ n*85/100 : ]
    test_y = y[ n*85/100 : ]
    return shared_data(train_x, train_y), shared_data(validate_x, validate_y), \
            shared_data(test_x, test_y)

if __name__ == '__main__':
    x, y, labels, labelHash,rowNames = readData('/home/lzh/experiments/w2v_lzh/text2vec/bin/docvecs.out')
    print labels
    print labelHash
    exit()
    print x
    for i in range(len(x)):
        print x[i], y[i], labels[y[i]]
    train, validate, test = generateShared(x, y)
    print train[0].get_value().shape[0]
    print validate[0].get_value().shape[0]
    print test[0].get_value().shape[0]

