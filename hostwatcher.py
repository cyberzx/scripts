import select
import socket
import json
import struct
import time

# polling thread

POLL_TIMEOUT = 5.0
ONLINE_TIMEOUT = 30.0
udpsock = None
pingmsg = struct.pack("B", 70)
servers_stats = {}

def init_socket():
  global  udpsock
  udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udpsock.settimeout(POLL_TIMEOUT)

def ping_servers(hosts, port_range):
  print "ping servers %s" % str(hosts)
  for host in hosts:
    if not host in servers_stats:
      servers_stats[host] = {}
    for port in port_range:
      if not port in servers_stats[host]:
        servers_stats[host][port] = {'state': 0,
                                    'online': False,
                                    'lastupd' : 0}
      udpsock.sendto(pingmsg, (host, port))

def recieve_answers():
  answer, addr = udpsock.recvfrom(16)
  if not addr[0] in servers_stats:
    servers_stats[addr[0]] = {}
  state = struct.unpack("B", answer[1])[0]

  servers_stats[addr[0]][addr[1]] = {'state': state, 
                                     'online': True, 
                                     'lastupd': time.clock()}

def print_stats():
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
  print "total: %d\nactive: %d" % (len(onlines), active)

def find_offline_servers():
  t = time.clock() - POLL_TIMEOUT
  for host in servers_stats.iterkeys():
    for port in servers_stats[host].iterkeys():
      info = servers_stats[host][port]
      if (t - info["lastupd"]) > ONLINE_TIMEOUT:
        info["online"] = False
  

def poll(hosts, port_range):
  ping_servers(hosts, port_range)
  while True:
    try:
      recieve_answers()
    except socket.timeout:
      find_offline_servers()
      print_stats()
      ping_servers(hosts, port_range)

init_socket()

servers_list=["94.198.52.129", "94.198.52.130", "94.198.52.131"]
poll(servers_list, range(5000, 5020))
  

