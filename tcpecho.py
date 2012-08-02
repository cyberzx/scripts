import socket
import  time

host = ''
port = 7852
backlog = 5
size = 4096
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
while 1:
    client, address = s.accept()
    data = []
    try:
      while 1:
        packet = client.recv(size)
        print "recieved packet %d bytes " % len(packet)
        data.append(packet)
        if len(packet) == 0
          break
    except:
      None
    
    print "recieved %d bytes " % len(data)
    if data:
        client.send(data)
    time.sleep(2)
    client.close() 

