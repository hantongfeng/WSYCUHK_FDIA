# -*- coding: utf-8 -*-
"""
Created on Fri May  4 14:17:26 2018

@author: Wang Shuoyao
"""

from __future__ import print_function
import tensorflow as tf
import numpy as np
import scipy.io as sio
import time
import math

def CNN_train(net,X_train,Y_train,X_valid,Y_valid,model_location,export_weight_biase_sw=0,regularizer=0.001,training_epochs=100, batch_size=100, LR= 0.001,in_keep=0.95,hi_keep=0.95,LRdecay=0):

    n_input = X_train.shape[1]                          # input size
    n_output = Y_train.shape[1]                         # output size
    num_train = X_train.shape[0]
    num_valid = X_valid.shape[0]
    print('train: %d ' % num_train, 'validation: %d ' % num_valid)

# setup and initialize the DNN network structure
    x = tf.placeholder("float", [None, n_input])
    y = tf.placeholder("float", [None, n_output])
    is_train = tf.placeholder("bool")

    learning_rate = tf.placeholder(tf.float32, shape=[])
    total_batch = int((X_train.shape[0]+X_valid.shape[0]) / batch_size)
    input_keep_prob = tf.placeholder(tf.float32)
    hidden_keep_prob = tf.placeholder(tf.float32)
    
    convsize=3;
    weights=[tf.Variable(tf.truncated_normal([convsize, 1,net[0]]) / np.sqrt(convsize))] 
    #net is input parameter of the size of the nerual network
    poolingsize=n_output
    print(poolingsize)
    poolingsize=int(math.ceil(float(poolingsize)/2))
    print(poolingsize)
    for i in range(len(net)-1):
        weights.append(tf.Variable(tf.truncated_normal([convsize,net[i], net[i+1]]) / np.sqrt(convsize)))
        poolingsize=int(math.ceil(float(poolingsize)/2))
        print(poolingsize)
    weights.append(tf.Variable(tf.truncated_normal([net[len(net)-1]*poolingsize, n_output]) / net[i]))

       
    biases=[tf.Variable(tf.ones([net[0]]) * 0.05)]
    for i in range(len(net)-1):
        biases.append(tf.Variable(tf.ones([net[i+1]]) * 0.05))
    biases.append(tf.Variable(tf.ones([n_output]) * 0.05))

    x1 = tf.nn.dropout(x, input_keep_prob)
    
    #print(x1)
    
   # print(x2)
    x1=tf.expand_dims(x1,2)
    for i in range(len(net)):
            #fil=tf.constant(1/3,dtype=tf.float32,shape=[3,1,len(net)])
            #x1=tf.expand_dims(x1,2)    
            #x1 = 
            #print(x2)
            #
            #print(x1)
            #print(x1,weights[i])
            x1= tf.nn.conv1d(x1,weights[i],stride=1,padding="SAME")
            #print(x1)
            #x1 = tf.add(, biases[i])   # x = wx+b
            x1 = tf.nn.relu(x1+biases[i])
            x1 = tf.layers.max_pooling1d(x1,2,2,padding='SAME')                                 # x = max(0, x)
            x1 = tf.nn.dropout(x1, hidden_keep_prob)            # dropout layer
            #print(x1)
    #print(x1, weights[len(net)])
    #x1=tf.squeeze(x1,2)
    print(x1)
    x_image=tf.reshape(x1,[-1,poolingsize*net[len(net)-1]])
    print(x_image)
    pred = tf.matmul(x_image, weights[len(net)]) + biases[len(net)]
    print(pred)
    #pred = tf.squeeze(pred,2)
# train the DNN
    if regularizer==0:
        cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels =y, logits = pred))
    else:
        cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels =y, logits = pred))
        for i in range(len(weights)):
            cost=cost+tf.contrib.layers.l2_regularizer(regularizer)(weights[i])

    optimizer = tf.train.AdamOptimizer(learning_rate, 0.09).minimize(cost)

    prediction = tf.sigmoid(pred)
    predicted_class = tf.greater(prediction, 0.5)
    correct = tf.equal(predicted_class, tf.equal(y,1.0))
    accuracy = tf.reduce_mean(tf.cast(correct, 'float'))

    init = tf.global_variables_initializer()
    saver = tf.train.Saver()

    with tf.Session() as sess:
        sess.run(init)
        start_time = time.time()

        for epoch in range(training_epochs):
            for i in range(total_batch):
                idx = np.random.randint(num_train,size=batch_size)
                #print(idx)
                if LRdecay==1:
                    _, c = sess.run([optimizer, cost], feed_dict={x: X_train[idx, :], y: Y_train[idx, :],
                                                                  input_keep_prob: in_keep, hidden_keep_prob: hi_keep,
                                                                  learning_rate: LR/(epoch+1), is_train: True})
                elif LRdecay==0:
                    _, c = sess.run([optimizer, cost], feed_dict={x: X_train[idx, :], y: Y_train[idx, :],
                                                                      input_keep_prob: in_keep, hidden_keep_prob: hi_keep,
                                                                      learning_rate: LR, is_train: True})


            if epoch%10==0:
                accu, y_valid = sess.run([accuracy, pred], feed_dict={x: X_valid, y: Y_valid, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False})

                print('epoch:%d, '%epoch, 'train:%0.4f'%accuracy.eval({x: X_train, y: Y_train, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}), 'tcost:%0.4f'%cost.eval({x: X_train, y: Y_train, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}),'validation:%0.4f:'%accuracy.eval({x: X_valid, y: Y_valid, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}),'vcost:%0.4f:'%cost.eval({x: X_valid, y: Y_valid, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}))
        print('epoch:%d, '%training_epochs, 'train:%0.4f'%accuracy.eval({x: X_train, y: Y_train, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}), 'tcost:%0.4f'%cost.eval({x: X_train, y: Y_train, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}),'validation:%0.4f:'%accuracy.eval({x: X_valid, y: Y_valid, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}),'vcost:%0.4f:'%cost.eval({x: X_valid, y: Y_valid, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}))

# export the parameters of the trained DNN, which is further reproduced in MATLAB
        if export_weight_biase_sw==1:
            WB={}
            WB.setdefault('weight_1',sess.run(tf.Print(weights[0],[n_input ,net[0]])))
            for a in range(len(net)-1):
                WB.setdefault('weight_%d'%(a+2),sess.run(tf.Print(weights[a+1],[net[a] ,net[a+1]])))
            WB.setdefault('weight_%d'%(len(net)+1),sess.run(tf.Print(weights[len(net)],[net[(len(net)-1)] ,n_output])))

            WB.setdefault('biase_1',sess.run(tf.Print(biases[0],[net[0]])))
            for a in range(len(net)-1):
                WB.setdefault('biase_%d'%(a+2),sess.run(tf.Print(biases[a+1],[net[a+1]])))
            WB.setdefault('biase_%d'%(len(net)+1),sess.run(tf.Print(biases[len(net)],[n_output])))


            sio.savemat('./data/weights_biases',WB)

        print("Training Time: %0.2f s" % (time.time() - start_time))

        saver.save(sess, model_location)

    return 0

# Functions for deep neural network testing
def CNN_test(net,X_test, Y_test,  model_location, save_name, binary=1):
    tf.reset_default_graph()

# setup and initialize the DNN network structure
    n_input = X_test.shape[1]                          # input size
    n_output = Y_test.shape[1]                         # output size
    with tf.name_scope('inputs'):
        x = tf.placeholder("float", [None, n_input])
        y = tf.placeholder("float", [None, n_output])
    is_train = tf.placeholder("bool")

    input_keep_prob = tf.placeholder(tf.float32)
    hidden_keep_prob = tf.placeholder(tf.float32)

    convsize=3;
    weights=[tf.Variable(tf.truncated_normal([convsize, 1,net[0]]) / np.sqrt(convsize))] 
    #net is input parameter of the size of the nerual network
    poolingsize=n_output
    poolingsize=int(math.ceil(float(poolingsize)/2))
    for i in range(len(net)-1):
        weights.append(tf.Variable(tf.truncated_normal([convsize,net[i], net[i+1]]) / np.sqrt(convsize)))
        poolingsize=int(math.ceil(float(poolingsize)/2))
    weights.append(tf.Variable(tf.truncated_normal([net[len(net)-1]*poolingsize, n_output]) / net[i]))

       
    biases=[tf.Variable(tf.ones([net[0]]) * 0.05)]
    for i in range(len(net)-1):
        biases.append(tf.Variable(tf.ones([net[i+1]]) * 0.05))
    biases.append(tf.Variable(tf.ones([n_output]) * 0.05))

    x1 = tf.nn.dropout(x, input_keep_prob)
    
    #print(x1)
    
   # print(x2)
    x1=tf.expand_dims(x1,2)
    for i in range(len(net)):
            #fil=tf.constant(1/3,dtype=tf.float32,shape=[3,1,len(net)])
            #x1=tf.expand_dims(x1,2)    
            #x1 = 
            #print(x2)
            #
            #print(x1)
            #print(x1,weights[i])
            x1= tf.nn.conv1d(x1,weights[i],stride=1,padding="SAME")
            #print(x1)
            #x1 = tf.add(, biases[i])   # x = wx+b
            x1 = tf.nn.relu(x1+biases[i])
            x1 = tf.layers.max_pooling1d(x1,2,2,padding='SAME')                                 # x = max(0, x)
            x1 = tf.nn.dropout(x1, hidden_keep_prob)            # dropout layer
            #print(x1)
    #print(x1, weights[len(net)])
    #x1=tf.squeeze(x1,2)
    x_image=tf.reshape(x1,[-1,poolingsize*net[len(net)-1]])
    pred = tf.matmul(x_image, weights[len(net)]) + biases[len(net)]

    prediction = tf.sigmoid(pred)
    predicted_class = tf.greater(prediction, 0.5)
    correct = tf.equal(predicted_class, tf.equal(y,1.0))
    accuracy = tf.reduce_mean(tf.cast(correct, 'float'))

    accuracy_symbol=0;
    for i in range (n_input):
        prediction1 = tf.sigmoid(pred[i,:])
        predicted_class1 = tf.greater(prediction1, 0.5)
        correct1 = tf.equal(predicted_class1, tf.equal(y[i,:],1.0))
        accuracy1 = tf.reduce_mean(tf.cast(correct1, 'float'))
        printvalue=tf.greater(accuracy1, 0.99)
       # print(printvalue.eval())
        if tf.greater(accuracy1, 0.99) is not None:
            accuracy_symbol+=1 
           # print(tf.greater(accuracy1, 0.99))
   # accuracy_symbol=accuracy_symbol/X_test.shape[0]
    print('Test Row Accuracy:', accuracy_symbol)

    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, model_location) # restore the saved DNN network

        start_time = time.time()
        y_pred = sess.run(pred, feed_dict={x: X_test, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False})

        testtime = time.time() - start_time

        if binary==1:
            print('Test Accuracy:', accuracy.eval({x: X_test, y: Y_test, input_keep_prob: 1, hidden_keep_prob: 1, is_train: False}))
           

 
            y_pred = tf.sigmoid(y_pred)
            y_pred = tf.greater(y_pred, 0.5)
            y_pred = tf.cast(y_pred, tf.int32)
            y_pred = y_pred.eval()

        sio.savemat(save_name, {'output_mode':Y_test,'output_mode_pred': y_pred})
    return testtime, y_pred