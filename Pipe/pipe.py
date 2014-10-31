# USAGE
# python loop.py | python pipe.py send cruncher
# python pipe.py listen cruncher


 
import socket
import sys

mode = sys.argv[1]
name = sys.argv[2]

dic = {"cruncher":8888}
port = dic[name]

if mode == "listen":

    # Create socket
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'Socket created'
    except socket.error, msg :
        print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
 
    # Bind socket
    try:
        s.bind(('', port))
    except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
     
    # Keep listening 
    while 1:
        d = s.recvfrom(1024)
        data = d[0]
        addr = d[1]
         
        if not data: 
            break
              
        print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
         
    s.close()

elif mode == "send":

    # create dgram udp socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    # Send
    while(1) :

        data = sys.stdin.readline()
        #print data
        #msg = raw_input('Enter message to send : ')        
         
        try :
            #Set the whole string
            s.sendto(data, ('', port))
         
        except socket.error, msg:
            print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

else:
    print "Wrong mode"