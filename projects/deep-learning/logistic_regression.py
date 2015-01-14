# -*- coding: utf-8 -*-
#author: BrightHush
#filename: logistic_regression.py

"""
Created on Sun Nov 16 21:37:43 2014
@author: BrightHush
Example for Logistic Regression
"""

import time

import numpy

import theano
import theano.tensor as T

import sys
sys.path.append('/home/lzh/experiments/ner/source/')

import data_io

rng = numpy.random

class LogisticRegression(object):
    def __init__(self, input, n_in):
        w_values = numpy.asarray(
                rng.uniform(
                    low=-numpy.sqrt(6./(n_in+2.0)),
                    high=numpy.sqrt(6./(n_in+2.0)),
                    size=(n_in, )),
                dtype=theano.config.floatX
                )
        self.w = theano.shared(
            value=w_values*4, 
            name='w', 
            borrow=True)
        
        self.b = theano.shared(value=.10, name='b')
        
        self.p_given_x = 1 / (1+T.exp(-T.dot(input, self.w) - self.b))
        self.y_given_x = self.p_given_x > 0.5
        
        self.params = [self.w, self.b]

    def negative_log_likelihood(self, y):
        ll = -y * T.log(self.p_given_x) - (1-y) * T.log(1 - self.p_given_x)
        cost = ll.mean() + 0.01 * (self.w ** 2).sum()
        return cost

    def errors(self, y):
        return T.mean(T.neq(self.y_given_x, y))

    def predict_single(self, x):
        p = 1 / (1 + T.exp(-T.dot(x, self.w) - self.b))
        y = p>0.5
        return [p, y]


def read_data():
    print 'load data...'    
    data = numpy.loadtxt('./titanic.dat', delimiter=',',  skiprows=8)
    x = []
    y = []
    for i in xrange(data.shape[0]):
        x.append(data[i,  : data.shape[1]-1])
        if data[i, -1]==-1.0:
            y.append(0)
        else:
            y.append(1)
    
    x = numpy.array(x)
    y = numpy.array(y)
    print '%d examples, %d columns every row' %(data.shape[0], data.shape[1])
    
    #normalize the fatures
    feature_min = x.min(0)    
    feature_max = x.max(0)
    x = x - numpy.array(feature_min)
    x = x / numpy.array(feature_max - feature_min)
    print x.min(0), x.max(0)
        
    return numpy.array(x), numpy.array(y)


def generate_data():
    rng = numpy.random
    N = 1000
    feats = 5
    D = (rng.randn(N, feats), rng.randint(size=N, low=0, high=2))
    x = D[0]
    y = D[1]
    
    x, y = read_data()
    #x, y = data_io.construct_input()

    def shared_data(data_x, data_y, borrow=True):        
        x_shared = theano.shared(numpy.asarray(data_x, 
                                           dtype=theano.config.floatX),
                                           borrow=borrow)
        y_shared = theano.shared(numpy.asarray(data_y, 
                                           dtype='int32'), #theano.config.floatX),
                                           borrow=borrow)
        return (x_shared, y_shared)
        #return (x_shared, T.cast(y_shared, 'int32'))

    n = x.shape[0]
    train_x = x[ : n*8/10, ]
    train_y = y[ : n*8/10, ]
    validate_x = x[ n*8/10:n*9/10, ]
    validate_y = y[ n*8/10:n*9/10, ]
    test_x = x[ n*9/10: , ]
    test_y = y[ n*9/10: , ]
    
    return [shared_data(train_x, train_y), 
            shared_data(validate_x, validate_y), 
            shared_data(test_x, test_y)]            
    
def sgd_optimization(learning_rate=0.13, n_epochs=1000, batch_size=100):
    dataset = generate_data()
    train_x, train_y = dataset[0]
    validate_x, validate_y = dataset[1]
    test_x, test_y = dataset[2]
    print type(test_x), type(test_y)

    print 'train set size %d' %(train_x.get_value().shape[0])
    print 'validate set size %d' %(validate_x.get_value().shape[0])
    print 'test set size %d' %(test_x.get_value().shape[0])    
    
    n_batches = train_x.get_value(borrow=True).shape[0] / batch_size
    
    index = T.lscalar()
    
    x = T.matrix('x')
    y = T.ivector('y')
    
    lr = LogisticRegression(x, train_x.get_value(borrow=True).shape[1])
    cost = lr.negative_log_likelihood(y)
    
    print 'compile function test_model...'
    test_model = theano.function(inputs=[index], 
                                 outputs=lr.errors(y), 
                                 givens={
                                    x : train_x[index*batch_size : (index+1)*batch_size], 
                                    y : train_y[index*batch_size : (index+1)*batch_size]
                                 })
    
    g_w = T.grad(cost=cost, wrt=lr.w)
    g_b = T.grad(cost=cost, wrt=lr.b)
    updates = [(lr.w, lr.w-learning_rate*g_w), 
               (lr.b, lr.b-learning_rate*g_b)]
    
    print 'complie function train_model...'
    train_model = theano.function(inputs=[index], 
                                  outputs=cost, 
                                  updates=updates, 
                                  givens={
                                      x : train_x[index*batch_size : (index+1)*batch_size],
                                      y : train_y[index*batch_size : (index+1)*batch_size]
                                  })

    print 'compile function prediction ...'
    single = T.matrix('single')
    single_index = T.iscalar('single_index')
    predict_single = theano.function(inputs=[single_index], 
                                 outputs=lr.predict_single(single), 
                                 givens={
                                     single : test_x[single_index : single_index+1]
                                     }
                                 )

    best_train_error = numpy.Inf    
    start_time = time.clock()
    for epoch in xrange(n_epochs):
        for minibatch_index in xrange(n_batches):
            batch_cost = train_model(minibatch_index)
            
        train_errors = [test_model(i) for i in xrange(n_batches)]
        train_error = numpy.mean(train_errors)
        if best_train_error > train_error:
            best_train_error = train_error
            
        print 'epoch %d, best_train_error %lf, train_error %lf' \
            %(epoch, best_train_error, train_error)
            #print 'iterator %d %lf' %(epoch*n_batches + minibatch_index+1, batch_cost)
    end_time = time.clock()
    print 'cost %d' %(end_time-start_time)


    print 'begin predicting...'
    test_x_np = test_x.get_value(borrow=True)
    test_y_np = test_y.get_value(borrow=True)
    print type(test_x_np), type(test_y_np)
    for i in range(test_x.get_value(borrow=True).shape[0]):
        print test_x_np[i, ], test_y_np[i]
        p, y = predict_single(i)
        print 'predicted ', p, y


if __name__ == '__main__':
    sgd_optimization()
    
