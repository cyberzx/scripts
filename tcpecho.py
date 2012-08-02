import socket

host = ''
port = 7852
backlog = 5
size = 4096
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
while 1:
    client, address = s.accept()
    data = client.recv(size)
    print "recieved %d bytes " % len(data)
    if data:
        client.send(data)
    client.close() 

