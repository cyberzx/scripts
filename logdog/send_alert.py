#!/usr/bin/python
import  errno
import  sys
import  os
import  smtplib 
import  email
import  select
import  fcntl

from email.mime import *
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject=""
send_to="example@example.com"
send_from = "example@example.com"
smtp_server= "example.com"
smtp_login = "login"
smtp_password="password"

def send_email(subject, message, from_addr, to_addr, smtp_addr,
              attachments = [], login = None, password = None ):
  """ send email"""
  
  msg = MIMEMultipart()
  msg['Subject'] = subject
  msg['From'] = from_addr
  msg.attach(MIMEText(message))

  if not isinstance(to_addr, list):
    to_addr = [to_addr]

  msg['Date'] = email.Utils.formatdate(localtime=True)
  msg['To'] = email.Utils.COMMASPACE.join(to_addr)

  for attach, data in attachments:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", 'attachment; filename="%s"' % attach)
    msg.attach(part)

  server = smtplib.SMTP(smtp_addr)
  if login != None and password != None:
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(login, password)
  server.sendmail(from_addr, to_addr, msg.as_string())
  server.close()

def main():
  fc = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
  fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fc | os.O_NONBLOCK)
 
  while True:
    try:
      input = sys.stdin.read() 
      if len(input) == 0:
        return
      print input
      send_email(subject,
                 input,
                 send_from, send_to,
                 smtp_server, [], smtp_login, smtp_password)
    except  IOError as e:
      if e.args[0] != errno.EAGAIN:
        return

    rlist, wlist, clist = select.select([sys.stdin], [], [])
    if len(clist) > 0:
      return


if __name__ == '__main__':
  sys.exit(main())
