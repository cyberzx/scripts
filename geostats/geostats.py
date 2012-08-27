#!/usr/bin/python
import GeoIP
import sys
import string

gi = GeoIP.open("/usr/share/GeoIP/GeoLiteCity.dat",GeoIP.GEOIP_STANDARD)
def geoiplookup(ip):
  return  gi.record_by_addr(ip)["country_name"]

def run():
  stats = {}
  for addr in sys.stdin.readlines():
    addr = string.replace(addr.strip(), "\n", "")
    country = geoiplookup(addr)
    if not country in stats:
      stats[country] = 1
    else:
      stats[country] += 1

  print stats
  
run()
