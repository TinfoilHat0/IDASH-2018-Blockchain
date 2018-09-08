from Savoir import Savoir
from sys import argv
from pickle import dumps
from collections import defaultdict
from math import floor
from time import time
from binascii import hexlify


def storeFile(chainInfo, filePath):
    ''' Store a file in the chain '''
    api = Savoir(chainInfo[0], chainInfo[1], chainInfo[2], chainInfo[3], chainInfo[4])
    streams = ['ts', 'node', 'id', 'ref_id', 'user', 'activity', 'resource']
    bufferStreams = {'tsBuffer':0, 'nodeBuffer':1, 'ref_idBuffer':3, 'userBuffer':4, 'activityBuffer':5, 'resourceBuffer':6}
    addr = api.getaddresses()[0]
    bucketSize = 10**7 # technically, tsBuffer is just bucketization
    # in order, tsBuffer, nodeBuffer ,.., resourceBuffer
    buffers = [defaultdict(list) for _ in range(7)] #id buffer is empty


    ctr, nodeID = 0, ""
    with open(filePath) as f:

        for log in f:
            parts = log[:-1].split('\t')
            nodeID = parts[1] # this should not change during the loop assuming every node submits their own files
            for i in range(5):
                parts[i] = int(parts[i])
            hexData = hexlify(dumps(parts)).decode()

            # log each tx one by one
            toPublish = []
            for i in range(7):
                streamName, key = streams[i], str(parts[i])
                if i != 2:
                    streamName += nodeID
                toPublish.append({'for':streamName, 'key':key, 'data':hexData})
            api.createrawsendfrom(addr , {}, toPublish, 'send')
            # fill buffers
            for buffer, index in bufferStreams.items():
                k, v = parts[index], hexData
                # tsBuffer case
                if buffer == 'tsBuffer':
                    k = floor(k/bucketSize)
                buffers[index][k].append(v)

            ctr += 1
            if ctr % 5000 == 0:
                print('Stored {} logs.'.format(ctr))

    # publish buffers
    sizeLimit = 10**4  #if buffer is too large tx might be rejected. hence we need a limit
    for buffer, index in bufferStreams.items():
        for k, v in buffers[index].items():
            if len(v) > sizeLimit:
                    lists = [v[i*sizeLimit:(i + 1)*sizeLimit] for i in range((len(v)+sizeLimit - 1) // sizeLimit)]
                    for l in lists:
                        api.publish(buffer+nodeID, str(k), hexlify(dumps(l)).decode())

            else:
                api.publish(buffer+nodeID, str(k), hexlify(dumps(v)).decode())


if __name__=='__main__':
    chainInfo = (argv[2], argv[3], 'localhost', argv[4], argv[1])
    filePath = argv[5].split('=')[1]
    print('Storing file...')
    start = time()
    storeFile(chainInfo, filePath)
    end = time()
    print('Storing {} elapsed {} seconds.'.format(filePath, end-start))
