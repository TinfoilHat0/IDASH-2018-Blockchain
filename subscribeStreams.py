from Savoir import Savoir
from sys import argv

def createStreams(chainInfo):
    '''
    Create the streams to store and efficiently retrieve the data.
    See: https://www.multichain.com/blog/2016/09/introducing-multichain-streams/
    '''
    api = Savoir(chainInfo[0], chainInfo[1], chainInfo[2], chainInfo[3], chainInfo[4])
    streams = ['ts', 'node', 'id', 'ref_id', 'user', 'activity', 'resource']
    bufferStreams = ['tsBuffer', 'nodeBuffer', 'ref_idBuffer', 'userBuffer', 'activityBuffer', 'resourceBuffer']

    for s in streams:
        if s != 'id':
            for i in range(1, 5):
                st = s + str(i)
                api.subscribe(st)
                print('Subscribed to stream {}'.format(st))
        else:
            api.subscribe(s)
            print('Subscribed to stream {}'.format(s))


    for s in bufferStreams:
        for i in range(1, 5):
            st = s + str(i)
            api.subscribe(st)
            print('Subscribed to stream {}'.format(st))

if __name__=='__main__':
    chainInfo = (argv[2], argv[3], 'localhost', argv[4], argv[1])
    createStreams(chainInfo)
