#!/usr/local/bin/python
# -*- coding: utf-8 -*-

'''
Created on Oct 26, 2014

Finding Progression Stages in Time-evolving Event Sequences WWW14
を実装してみる．

X =: [x_0,x_1,...,x_i,...,x_n]
numN : len(X)
x_i : [x_i_0,x_i_1,...,x_i_j,...,x_i_numLs[i]]
numLs[i]: len(x_i)
x_i_j: one event in c
s_i_j: in {0,..,numK-1} s.t. j>=k => s_i_j >= s_i_k

numC : the number of classes
numK : the number of stages
numM : the number of possivle(different) event
numL : sum(numLs)

c = [c_1, c_2,...,c_numN]  
c_i : in {0,...,numC-1}

dirLambda : dirichlet distribution parameter lambda


@author: ochi
'''

import numpy as np
import csv

random_seed = 2014

idEventFile   = "sample-id-event.csv"
userEventFile = "sample-user-eventId.csv"

def readIdEventFile():
    f = open(idEventFile, 'r')
    reader = csv.reader(f)
    fieldnames = next(reader)
    eventNames = []
    for data in reader:
        eventNames.append(data[1])
    f.close()
    return eventNames

def readXFile():
    f = open(userEventFile, 'r')
    reader = csv.reader(f)
    fieldnames = next(reader)
    eventLogs = []
    userIds = []
    for data in reader:
        eventLog = []
        for a_data in data[1:]:
            eventLog.append(int(a_data))
        eventLogs.append(eventLog)
        userIds.append(int(data[0]))
    f.close()
    return userIds,eventLogs

def printTransX(X,userIds,eventNames):
    for i in range(len(X)):
        print "%d,"%(userIds[i]),
        for j in range(len(X[i])):
            if j < len(X[i])-1:
                print "%s,"%(eventNames[X[i][j]]),
            else:
                print "%s"%(eventNames[X[i][j]])


def run():
    numC = 8
    numK = 4
    dirLambda = 1.0 

    eventNames = readIdEventFile()
#    print "eventNames"
#    print eventNames
    maxEventId = len(eventNames) - 1
    numM = len(eventNames)
    userIds,X = readXFile()
#    print "X"
#    print X
#    X = [[0,1,3,5,7],[1,2,4],[6,7]] # read a data file 各x_iは0から始まるイベントIDがintで入る.

    
    np.random.seed(random_seed)
    c = np.random.randint(0,numC,len(X))
    s = initialize_s(X, numK)

    theta = sampleTheta(numC,numK,numM,dirLambda)
    likelihood = calcLikelihood(X,c,s,theta)
    print "likelihood: %.6f"%(likelihood)
    
    before_likelihood = 0

    loop_c = 0
    while abs((before_likelihood-likelihood) / likelihood) > 0.001:
        print "loop_c:%d"%(loop_c)
        before_likelihood = likelihood
        theta = updateTheta(X,c,s,numC,numK,numM,dirLambda)
        c,s = updateStages(X,numC,numK,numM,dirLambda,theta)
        likelihood = calcLikelihood(X,c,s,theta)
        loop_c += 1
        print "likelihood: %.6f"%(likelihood)

    print "X"
    print X
    print "transX"
    printTransX(X,userIds,eventNames)
    print "c"
    print c
    print "s"
    print s


def initialize_s(X,numK):
    # paper 2.3 algorithm initialization
    s = []
    for i in range(len(X)):
        lenXi = len(X[i])
        unit = lenXi / numK
        odd = lenXi % numK
        s_i = []
        for k in range(numK):
            if odd > 0:
                s_i += [k]*(unit+1)
                odd -= 1
            else:
                s_i += [k]*unit
        s.append(s_i)
    return s

def sampleTheta(numC,numK,numM,dirLambda):
    theta = []
    for p in range(numC):
        theta_p = []
        for q in range(numK):
            theta_p_q = np.random.dirichlet(([dirLambda]*numM),1)[0]
            theta_p.append(theta_p_q)
        theta.append(theta_p)
    return theta

def updateTheta(X,c,s,numC,numK,numM,dirLambda):
    theta = []
    for p in range(numC):
        theta_p = []
        for q in range(numK):
            summation_xij_array = calcSummation_xij_array(X,p,q,c,s,numM)
            summation_xij = sum(summation_xij_array)
            theta_p_q = [0]*numM
            for r in range(numM):
                theta_p_q[r] =  (float(dirLambda) + summation_xij_array[r]) / (float(numM*dirLambda)+summation_xij)
            theta_p.append(theta_p_q)
        theta.append(theta_p)
    return theta

def calcSummation_xij_array(X,p,q,c,s,numM):
    # summation_xij_array = [0]*numM
    summation_xij_array = [0]*numM
    for i in range(len(X)):
        x_i = X[i]
        for j in range(len(x_i)):
            x_ij = x_i[j]
            r = x_ij
            if c[i] == p and s[i][j] == q:
                summation_xij_array[r] += 1
    return summation_xij_array

def calcCost(p,q,r,theta):
    cost = np.log(theta[p][q][r])
    return cost

def calcG(p,j,s,theta,stage_path,x_i):
    if j > 0:
        if s > 0:
            cost_same_s = calcG(p,j-1,s,theta,stage_path,x_i)+calcCost(p,s,x_i[j],theta)
            cost_before_s = calcG(p,j-1,s-1,theta,stage_path,x_i)+calcCost(p,s,x_i[j],theta)
            if cost_same_s >= cost_before_s:
                stage_path[j-1] = s
                return cost_same_s
            else:
                stage_path[j-1] = s-1
                return cost_before_s
        else:
            cost = calcCost(p,s,x_i[j],theta)
            cost_same_s = calcG(p,j-1,s,theta,stage_path,x_i)+calcCost(p,s,x_i[j],theta)
            stage_path[j-1] = s
            return cost_same_s
    else:
        return calcCost(p,s,x_i[j],theta)

def updateStages(X,numC,numK,numM,dirLambda,theta):
    updated_c = []
    updated_s = []

    for i in range(len(X)):
        x_i = X[i]
        lastIdx = len(x_i)-1
        category_loglikelihood_cs_i = []
        category_stage_paths = []
        for category in range(numC):
            loglikelihood_cs_i = []
            stage_paths = []
            for last_stage in range(numK):
                stage_path = [0]*len(x_i)
                stage_path[lastIdx] = last_stage
                g_last_stage = calcG(category,lastIdx,last_stage,theta,stage_path,x_i)

                loglikelihood_cs_i.append(g_last_stage)
                stage_paths.append(stage_path)
            max_loglikelihood_cs_i_index = loglikelihood_cs_i.index(max(loglikelihood_cs_i))
            max_stage_path = stage_paths[max_loglikelihood_cs_i_index]

            category_loglikelihood_cs_i.append(max_loglikelihood_cs_i_index)
            category_stage_paths.append(max_stage_path)

        max_category_loglikelihood_cs_i_index = category_loglikelihood_cs_i.index(max(category_loglikelihood_cs_i))
        max_category_stage_paths = category_stage_paths[max_category_loglikelihood_cs_i_index]

        updated_c.append(max_category_loglikelihood_cs_i_index)
        updated_s.append(max_category_stage_paths)

    return updated_c,updated_s

def calcLikelihood(X,c,s,theta):
    likelihood = 0.0
    for i in range(len(X)):
        x_i = X[i]
        for j in range(len(x_i)):
            x_ij = x_i[j]

            likelihood += np.log(theta[c[i]][s[i][j]][x_ij])
    return likelihood


if __name__ == "__main__":
    run()
