#!/usr/local/bin/python
# -*- coding: utf-8 -*-

'''
Created on Oct 28, 2014

Progression Stage Modelの実装を試す用のCSVデータを吐き出すスクリプト

@author: ochi
'''

import csv
import random

random_seed = 2014

idEventFile = "sample-id-event.csv"
numUser = 100
maxEventLength = 20
minEventLength =  2

outputFile = "sample-user-eventId.csv"

def run():
    random.seed(random_seed)
    eventNames = readIdEventFile()
    maxEventId = len(eventNames) - 1

    userEventLogs = []
    for i in range(numUser):
        eventLog = []
        eventLength = random.randint(minEventLength,maxEventLength)
        for j in range(eventLength):
            eventId = random.randint(0,maxEventId)
            eventLog.append(eventId)
        userEventLogs.append(eventLog)

    # 書き込み
    g = open(outputFile, 'w')
    w = csv.writer(g, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    w.writerow(["userId","Events"])
    for u_id in range(len(userEventLogs)):
        eLog = userEventLogs[u_id]
        row = [u_id]+eLog
        w.writerow(row)
    g.close()

    return   

def readIdEventFile():
    f = open(idEventFile, 'r')
    reader = csv.reader(f)
    fieldnames = next(reader)
    eventNames = []
    for data in reader:
        eventNames.append(data[1])
    f.close()
    return eventNames


if __name__ == "__main__":
    run()
