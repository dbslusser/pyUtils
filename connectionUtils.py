#! /usr/bin/python

"""
Description:
    Collection of tools to manage connections to devices

Author:
    David Slusser

Revision:
    0.0.1
"""

import sys
import os
import time
import telnetlib
import paramiko
from scp import SCPClient
import socket
import select
import logging
import StringIO
import re


class TelnetController():
    """
    Description:
        Connect to remote host with TELNET and issue commands.

    Parameters:
        host     - hostname or ip address of remote host
        port     - port number
        timeout  - timeout (in seconds) 
        user     - user name
        password - password
        prompt   - command prompt
        
    """
    def __init__(self, host, user, password=None, port=23, timeout=300, prompt=":~$"):
        """ class entry point """
        self.host = host
        self.user = user
        self.password = password
        self.timeout = timeout
        self.prompt = prompt
        self.hdl = None
        self.connect()

    def connect(self):
        """ Connect to a remote host and login """
        try:
            self.hdl = telnetlib.Telnet(self.host)
            self.hdl.read_until("login: ")
            self.hdl.write(self.user + "\n")
            if self.password:
                self.hdl.read_until("Password: ")
                self.hdl.write(self.password + "\n")
                self.hdl.read_until(self.prompt)
        except socket.timeout:
            print "failed to connect to %s" % self.host

    def connectDirect(self):
        """ Connect to a remote host (not expecting login) """
        try:
            self.hdl = telnetlib.Telnet(self.host)
        except socket.timeout:
            print "failed to connect to %s" % self.host
            
    def run(self, cmd, prompt=None):
        """
        Description:
            Run a command on the remote host.
        
        Parameters:
            command  - command to execute
            prompt   - expected prompt after execution
            
        Returns:
            string of command response
        """ 
        if not prompt:
            prompt = self.prompt
        if not cmd.endswith("\n"):
            cmd += "\n"
        time.sleep(1)
        self.hdl.write(cmd)
        return self.hdl.read_until(prompt, self.timeout)

    def close(self):
        """ Close the connection to the remote host """
        self.hdl.write("exit\n") 
        self.hdl.close()


class SshController():
    """
    Description:
        Connect to remote host with SSH and issue commands.

    Parameters:
        host     - hostname or ip address of remote host
        port     - port number
        timeout  - timeout (in seconds) 
        user     - user name
        password - password
    """

    def __init__(self, host, user, password, port=22, timeout=300):
        """ Class entry point """
        self.type = "ssh"
        self.host = host
        self.port = int(port)
        self.timeout = int(timeout)
        self.user = user
        self.password = password
        self.hld = None
        self.ec = None
        self.connect()

    def connect(self):
        """ Establish handler to remote host """
        try:
            self.hdl = paramiko.SSHClient()
            self.hdl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.hdl.connect(self.host, self.port, username=self.user, password=self.password)
            self.trans = self.hdl.get_transport()
            self.trans.window_size = 2147483647
            self.scp = SCPClient(self.trans)

        except paramiko.AuthenticationException:
            logging.error("We had an authentication exception!")

        except Exception, msg:
            try:
                self.ch.close()
                self.trans.close()
                self.trans.stop_thread()
            except:
                self.destroy()
            logging.info("Failed to connect to %s. %s" % (self.host, msg))
        logging.info("connection to %s open.", self.host)
        return

    def destroy(self):
        """ destroy handler """
        if 'ch' in dir(self):
            del self.ch
        if 'trans' in dir(self):
            del self.trans
        if 'hdl' in dir(self):
            del self.hdl   
        
    def flush(self, chan):
        """ Read everything from the channel """
        time.sleep(1)
        resp = self.read(chan)
        return resp

    def read(self, chan, timeout=None):
        """ Retrieves everything from the channel buffer """
        if not timeout:
            timeout = self.timeout
        buf = str()
        try:
            resp = chan.recv(5000)
            while resp:
                buf += resp
                resp = chan.recv(5000)
        except socket.timeout: # This is resp_wait.
            logging.error("command timeout '%s' exceeded" % timeout)
            pass
        return buf

    def write(self, cmd, chan):
        """ send a command to the channel """
        chan.exec_command(cmd)
        chan.sendall(cmd)

    def run(self, cmd, timeout=None, sudo=False):
        """ Send a command and return the response """
        if not timeout:
            timeout = self.timeout
        chan = self.trans.open_session()
        chan.settimeout(timeout)
        if sudo:
            cmd = "echo %s | sudo -S %s" % (self.password, cmd)
        self.write(cmd, chan)
        resp = self.read(chan, timeout)
        chan.close()
        return resp

    def killProcess(self, p):
        """ find a process by name/command and kill it"""
        resp = self.run("ps -ef | grep %s" % p)
        resp_list = [i for i in resp.splitlines() if "grep" not in i]
        if len(resp_list) > 1:
            logging.error("could not determine PID to kill")
            return 1
        else:
            pid = resp_list[0].split()[1]
            self.run("kill %s" % pid)


    def get(self, src, dst):
        """ Get a file from a remote" location """
        self.scp.put(src, dst)
    
    def put(self, src, dst):
        """ Put a file on a remote location """
        self.scp.put(src, dst)
   
    def close(self):
        self.trans.close()
        self.trans.stop_thread()
        logging.info("connection to %s closed.", self.host)


class NetconfController():
    """
    Description:
        Connect to remote host via netconf and issue commands.

    Parameters:
        host     - hostname or ip address of remote host
        port     - port number
        timeout  - timeout (in seconds) 
        user     - user name
        password - password   
    """
    
    def __init__(self, host, user, password, port=830, timeout=300):
        """ Class entry point """
        self.type = "netconf"
        self.host = host
        self.port = int(port)
        self.timeout = int(timeout)
        self.user = user
        self.password = password
        self.hld = None
        self.connect()
        self.flush()
        self.hello()
        
    def connect(self):
        """ Creates a NETCONF connection. """
        try:
            self.hdl = paramiko.SSHClient()
            self.hdl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.hdl.connect(self.host, self.port, username=self.user,password=self.password)
            self.trans = self.hdl.get_transport()
#             self.trans.window_size = 2147483647            
            self.ch = self.trans.open_session()
            self.ch.setblocking(0)
            self.ch.settimeout(self.timeout)
            self.ch.invoke_subsystem('netconf')

        except Exception,msg:
            try:
                self.ch.close()
                self.trans.close()
                self.trans.stop_thread()
            except:
                pass
            print "Failed to connect to %s" % msg
            sys.exit(1)

    def flush(self):
        """ read everything in the buffer """
        time.sleep(2)
        resp = self.read()
        return

    def read(self):
        """ Retrieves everything from the buffer. """
        buf = str()
        try:
            resp = self.ch.recv(5000)
            while resp:
                buf += resp
                resp = self.ch.recv(5000)
                if resp.find('</rpc-reply>') == 0:
                    break
        except socket.timeout:
            pass
        return buf
    
    def write(self, cmd):
        """ Writes a message to the channel """
        if not cmd.endswith("]]>]]>"):
            cmd += "]]>]]>"        
#         self.ch.send(cmd)
        self.ch.sendall(cmd)

    def run(self, cmd):
        self.write(cmd)
        return self.read()

    def hello(self):
        cmd = """<?xml version="1.0" encoding="UTF-8"?>
  <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
  <capability>urn:ietf:params:netconf:base:1.0</capability>
    </capabilities>
  </hello>]]>]]>"""
        self.write(cmd)
        return
    
    def close(self):
        """ Close the connection to the remote host """
        self.write("""<rpc><close-session/></rpc>""")
        self.write("""<rpc><kill-session/></rpc>""")
        self.ch.close()
        self.trans.close()
        self.trans.stop_thread()
        logging.info("connection to %s closed.", self.host)


class SocketController():
    """ 
    Description:
        Connect to remote host and issue commands.

    Parameters:
        host     - hostname or ip address of remote host
        port     - port number
        timeout  - timeout (in seconds)
        echo     - echo commands
        buffer   - buffer size (in bytes) 
    """
    
    def __init__(self, host, port, timeout=15, echo=True, buff=128):
        """ Class entry point """
        self.host = host
        self.port = port
        self.timeout = timeout #float(timeout)
        self.echo = echo
        self.buffer = buff
        self.hdl = None
        self.connect()

    def connect(self):
        """ Establish handler to remote host """
        try:
            self.hdl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.hdl.settimeout(self.timeout)
            self.hdl.connect((self.host, self.port))
        except socket.error as e:
            logging.error("Failed to connect to %s", self.host)
            self.close()

    def write(self, cmd):
        """ send a command to the host """
        if self.hdl is None: 
            raise IOError('disconnected')
            self.close()
        try:
            if not cmd.endswith("\n"):
                cmd += "\n"
            self.hdl.send(cmd)
        except IOError as e:
            raise e

    def read(self, wait=1):
        if self.hdl is None: 
            raise IOError('disconnected')
            self.close()
        
        buf = ""#bytearray()
        data = True
        while data:
            r,w,e = select.select([self.hdl], [], [self.hdl], wait)
            if r: # socket readable               
                data = self.hdl.recv(self.buffer)
                if data: 
                    buf += data
                else: # Socket readable but there is no data, disconnected.
                    data = False
#                     self.close()
            else: # no data in socket
                data = False
        return buf

    def readUntil(self, prompt='(\d+|-\d+), ".*"', timeout=25):
        """
        Description:
            Retrieves data the buffer until <prompt> 
        
        Parameters:
            prompt - regular expression of expected expected prompt or text
            
        Returns:
            string of buffer contents 
        """
        self.hdl.settimeout(timeout)
        resp = ""
        try:
            while not resp:
                resp = self.hdl.recv(128)
                mo = re.search(prompt, resp)
                if mo:
                    break
        except socket.timeout:
            logging.error("timeout exceeded")
            pass
        return resp

    def run(self, cmd, wait=0.25):
        """
        Description:
            Run a command on the remote host and return the response.
        
        Parameters:
            command  - command to execute
            
        Returns:
            string of command response
        """
        if self.hdl is None: 
            raise IOError('disconnected')
            self.close()
        if self.echo:
            print "executing: %s" % cmd
        self.write(cmd)
        return self.read(wait)
    
    def close(self):
        """ Close the connection to the remote host """
        if self.hdl is None: 
            logging.debug("socket is already closed.")
            return
        self.hdl.close()
        self.hdl = None
