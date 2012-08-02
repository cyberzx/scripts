import select
import socket
import json
import struct
import time
from  collections import deque

POLL_TIMEOUT   = 5.0
TOUCH_INTERVAL= 5.0
ONLINE_TIMEOUT = 120.0
TOUCH_MESSAGE  = struct.pack("B", 69)


def print_stats(servers_stats):
  total = 0
  active = 0
  
  onlines = []
  offlines = []
  for host in servers_stats.iterkeys():
    for port in servers_stats[host].iterkeys():
      info = servers_stats[host][port]
      state = info['state']
      online = info['online']
      if online:
        onlines.append((host, port, state))
      else:
        offlines.append((host, port))
      total += 1
      if state == 1 and online:
        active += 1

  print "-----------------------------------"
  print "online: "
  for info in onlines:
    print "%s:%d -> %d" % info
  print "-----------------------------------"
  print "offline: "
  for info in offlines:
    print "%s:%d" % info
  print "-----------------------------------"
  print "total: %d\nactive: %d\nonline: %d\noffline: %d" % (total, active, len(onlines), len(offlines))

def ping_servers(hosts, ports):
  udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udpsock.setblocking(0)

  servers_stats = {}
  hostslist = deque(reduce(lambda x, y: x + y,
                        map(lambda h: 
                          map (lambda p: (h, p), ports),
                            hosts)))
  for host, port in hostslist:
    if not host in servers_stats:
      servers_stats[host] = {}
    servers_stats[host][port] = {'state': 0,
                                 'online': False,
                                 'lastupd' : 0}
  

  def find_offline_servers():
    t = time.clock() - POLL_TIMEOUT
    for host in servers_stats.iterkeys():
      for port in servers_stats[host].iterkeys():
        info = servers_stats[host][port]
        if (t - info["lastupd"]) > ONLINE_TIMEOUT:
          info["online"] = False
  
  def recieve_answers():
    try:
      answer, addr = udpsock.recvfrom(16)
      if not addr[0] in servers_stats:
        servers_stats[addr[0]] = {}
      state = struct.unpack("B", answer[1])[0]

      servers_stats[addr[0]][addr[1]] = {'state': state, 
                                         'online': True, 
                                         'lastupd': time.clock()}
    except socket.error:
      None

  def touch_servers():
    n = 0
    try:
      while n < len(hostslist):
        udpsock.sendto(TOUCH_MESSAGE, hostslist[n])
        n+=1
      print("touch %d servers: " % n)
      return  True
    except socket.error:
      print("touch %d servers: " % n)
      print("write blocked")
      hostslist.rotate(n)
      return  False

  lastprinttime = 0
  lasttouchtime = -TOUCH_INTERVAL
  while True:
    writeBlock = False
    
    touchDT = time.clock() - lasttouchtime
    if touchDT > TOUCH_INTERVAL:
      writeBlock = not touch_servers()
      lasttouchtime = time.clock()

    rlist, wlist, xlist = select.select([udpsock], [udpsock], [udpsock], POLL_TIMEOUT)
    if len(rlist) > 0:
      recieve_answers()
    if len(wlist) > 0 and writeBlock:
      touch_servers()

    if time.clock() - lastprinttime > 4.0:
      find_offline_servers()
      print_stats(servers_stats) 
      lastprinttime = time.clock()
  

servers_list=["94.198.52.129", "94.198.52.130", "94.198.52.131"]
servers_list=["94.198.52.131"]
ping_servers(servers_list, range(5000, 5050))
  

