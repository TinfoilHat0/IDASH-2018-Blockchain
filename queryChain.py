from Savoir import Savoir
from sys import argv, maxsize, stdout
from binascii import hexlify, unhexlify
from pickle import dumps, loads
from collections import defaultdict
from operator import itemgetter
from math import floor
from time import time
import multiprocessing as mp


class ChainQuery:
    def __init__(self, chainInfo, ranges, fields, sortKey, sortOrder):
        self.api = Savoir(chainInfo[0], chainInfo[1], chainInfo[2], chainInfo[3], chainInfo[4])
        self.ranges = ranges
        self.fields =  fields
        self.sortKey = sortKey
        self.sortOrder = sortOrder
        self.logIndexes = {'timestamp':0, 'node':1, 'id':2, 'ref_id':3, 'user':4, 'activity':5, 'resource':6}
        self.bucketSize = 10**7
        self.sizeLimit = 10**4


    def deserialize(self ,d):
        data = d['data']
        if type(data) is dict:
            txid, vout = data['txid'], data['vout']
            return loads(unhexlify(self.api.gettxoutdata(txid, vout)))
        else:
            return loads(unhexlify(data))


    def recoverBucket(self, bufferStream, stream, bufferSize, ts_start, ts_end):
        ''' Add missing items from tsStream to bucketStream '''
        bucketDict = defaultdict(list)
        for i in self.api.liststreamitems(stream, False, 9999999, bufferSize, True):
            log = loads(unhexlify(i['data']))
            if log[0] >= ts_start and log[0] <= ts_end:
                self.rangeLogs.append(i['data'])
                bucketDict[floor(log[0]/self.bucketSize)].append(i['data'])
        for k, v in bucketDict.items():
            self.api.publish(bufferStream, str(k), hexlify(dumps(v)).decode())


    def getBuckets(self, stream, start, end):
        # Range query via bucketization
        startBucketKey, endBucketKey = floor(start/self.bucketSize),  floor(end/self.bucketSize)
        nBucketItems = 0
        for i in self.api.liststreamkeys(stream, '*', False, 9999999):
            bucketKey = i['key']
            if int(bucketKey) == startBucketKey or int(bucketKey) == endBucketKey:
                for d in self.api.liststreamkeyitems(stream, bucketKey, False, 9999999, 0, True):
                    bucket = self.deserialize(d)
                    nBucketItems += len(bucket)
                    for hexData in bucket:
                        timestamp = loads(unhexlify(hexData))[0]
                        if timestamp > end:
                            break
                        elif timestamp >= start and timestamp <= end:
                            self.rangeLogs.append(hexData)
            else:
                for d in self.api.liststreamkeyitems(stream, bucketKey):
                    bucket = self.deserialize(d)
                    nBucketItems += len(bucket)
                    if int(bucketKey) > startBucketKey and int(bucketKey) < endBucketKey:
                        self.rangeLogs += bucket
        self.bucketSizes.append(nBucketItems)


    def rangeQuery(self, start=0, end=maxsize):
        ''' Fetch the logs whose ts is between start and end '''
        self.rangeLogs, self.bucketSizes = [], []
        for i in range(1, 5):
            self.getBuckets('tsBuffer{}'.format(i), start, end)

        for i in range(1, 5):
            tsSize = self.api.liststreams('ts{}'.format(i))[0]['items']
            if tsSize > self.bucketSizes[i-1]:
                self.recoverBucket('tsBuffer{}'.format(i), 'ts{}'.format(i), self.bucketSizes[i-1], start, end)


    def filterLogs(self, possibleMatches):
        # convert ts,node,ref_id,user to integer for comparison
        for k, v in self.fields.items():
            if k in ['node', 'id', 'ref_id', 'user']:
                self.fields[k] = int(v) if v.isdigit() else None
        result = []
        for log in possibleMatches:
            parts, isMatch = loads(unhexlify(log)), True
            if self.selectField != 'ts':
                isMatch = parts[0] >= ranges[0] and parts[0] <= ranges[1]
            if isMatch:
                for k, v in self.fields.items():
                    if parts[self.logIndexes[k]] != v:
                        isMatch = False
                        break
            if isMatch:
                result.append(parts)
        if self.sortKey:
            result = sorted(result, key=itemgetter(self.logIndexes[self.sortKey]), reverse=self.sortOrder)
        for line in result:
            print('\t'.join(map(str, line)))


    def publishBuffer(self, buffer, bufferName, key):
        if len(buffer) < self.sizeLimit:
            self.api.publish(bufferName, key, hexlify(dumps(buffer)).decode())
            return

        lists = [buffer[i*self.sizeLimit:(i + 1)*self.sizeLimit] for i in range((len(buffer)+self.sizeLimit - 1) // self.sizeLimit)]
        for l in lists:
            self.api.publish(bufferName, key, hexlify(dumps(l)).decode())



    def processQuery(self):
        ''' Process the query, output the result to terminal '''
        matchCounts = defaultdict(int)
        if isRangeQuery or not self.fields:
            self.rangeQuery(self.ranges[0], self.ranges[1]) #range query can also be used to get all records efficiently
            matchCounts['ts'] = len(self.rangeLogs)

        for k, v in self.fields.items():
            if k == 'id':
                matchCounts[k] = self.api.liststreamkeys(k, v)[0]['items']
            else:
                for i in range(1, 5):
                    matchCounts[k] += self.api.liststreamkeys(k+'{}'.format(i), v)[0]['items']

        self.selectField = min(matchCounts, key=matchCounts.get)
        if self.selectField == 'ts':
            return self.filterLogs(self.rangeLogs)

        idLogs=[]
        if self.selectField == 'id':
            for d in self.api.liststreamkeyitems(self.selectField, self.fields[self.selectField], False, 9999999):
                idLogs.append(d['data'])
            return self.filterLogs(idLogs)

        fieldLogs = []
        for i in range(1, 5):
            for d in self.api.liststreamkeyitems(self.selectField+'Buffer{}'.format(i), self.fields[self.selectField], False, 9999999):
                fieldLogs += self.deserialize(d)
            streamCnt = self.api.liststreamkeys(self.selectField+'{}'.format(i), self.fields[self.selectField])[0]['items']
            if streamCnt > len(fieldLogs):
                buffer = []
                for d2 in self.api.liststreamkeyitems(self.selectField+'{}'.format(i), self.fields[self.selectField], False, 9999999, len(fieldLogs), True):
                    fieldLogs.append(d2['data'])
                    buffer.append(d2['data'])
                self.publishBuffer(buffer, self.selectField+'Buffer{}'.format(i), self.fields[self.selectField])
        return self.filterLogs(fieldLogs)


if __name__=='__main__':
    ranges, fields = [0, maxsize], {}
    sortKey, sortOrder = '', False
    isRangeQuery =  False
    for s in argv[5:]:
        k, v = s.split('=')
        if k in ['node', 'id', 'ref_id', 'user', 'activity', 'resource'] and v:
            fields[k] = v
        elif k == 'startTime' and v:
            ranges[0] = int(v) if v.isdigit() else ranges[0]
            isRangeQuery = True
        elif k == 'endTime' and v:
            ranges[1] = int(v) if v.isdigit() else ranges[1]
            isRangeQuery = True
        elif k == 'sortKey' and v:
            sortKey = v
        elif k == 'sortOrder':
            sortOrder = True if v == 'desc' else False


    chainInfo = (argv[2], argv[3], 'localhost', argv[4], argv[1])
    queryTool = ChainQuery(chainInfo, ranges, fields, sortKey, sortOrder)
    queryTool.processQuery()
