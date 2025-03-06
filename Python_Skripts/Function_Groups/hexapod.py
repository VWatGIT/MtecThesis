#from pylablib.devices import Thorlabs # TODO uncomment later
import numpy as np
import socket
import time
from configparser import ConfigParser
import os
import threading

class Hexapod():
    def __init__(self):
        # Hexapod Travel Ranges
        self.travel_ranges = {
            # theoretical ranges for single axes
            # all in +- mm
            'X': 50,
            'Y': 50,
            'Z': 20,
            'U': 15,
            'V': 15,
            'W': 30,
        }

        # Load Configuration
        config = ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_path)


        self.IP = str(config.get('Hexapod', 'IP')) 
        self.port_1 = config.getint('Hexapod', 'port_1') # Server
        self.port_2 = config.getint('Hexapod', 'port_2') # Stopper

        self.socket_timeout = config.getfloat('Hexapod', 'socket_timeout')

        for key in self.travel_ranges.copy().keys():
            self.travel_ranges[key] = config.getint('Hexapod', key)
        



        # Command Dictionary
        self.commands = {
            'set_sub_folder': 'setSubFolder Huehnerherz/2_Vascularized/Tracking/Hexapod/blabla/',
            'get_pos': 'get_pos',
            'set_local_file_name': 'setLocalFileName testfolder2',
            'start_rt_local': 'startRTLocal',
            'stop_rt_local': 'stopRTLocal',
            'set_vel ': 'set_vel ', # + str(vel),
            'disconnect': 'disconnect',
            'quit': 'quit',
            'stop': 'stop'
        }
        
        self.default_position = [0, 0, 0, 0, 0, 0] # [x, y, z, roll, pitch, yaw]
        
        self.position = [0, 0, 0, 0, 0, 0] # [x, y, z, roll, pitch, yaw]
        self.velocity = 1 # mm/s Default

        # Set up Sockets to connect to Server later
        self.tcpipObj_Hexapod_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket for Commands
        self.tcpipObj_Hexapod_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket for Emergency Stop

        # Set socket timeouts
        self.tcpipObj_Hexapod_1.settimeout(self.socket_timeout)  # Set timeout to 5 seconds
        self.tcpipObj_Hexapod_2.settimeout(self.socket_timeout)  # Set timeout to 5 seconds


        self.connecting = False
        self.connection_status = False
        #self.connect_sockets()

        if self.connection_status is True:
            self.move_to_default_position()
    
    def move_to_default_position(self):
        if not self.connection_status:
            rcv = 'Hexpod not connected to server'
            return rcv

        rcv = self.move(self.default_position, flag = "absolute")
        return rcv
    
    def connect_sockets(self, callback = None):
        # Connect to Hexapod Server
        """
        Expects callback function as input argument
        callback(rcv) is called after connection attempt
        """

        if callback is None:
            #print('No callback function provided')
            callback = lambda x: print(x)

        if self.connecting:
            rcv = 'Already connecting to server'
            callback(rcv)
            return rcv
        
        if self.connection_status:
            rcv = 'Already connected to server'
            callback(rcv)
            return rcv
        
        
        #connection_thread = threading.Thread(target=self._connect, args=(callback,))
        #connection_thread.start()
        rcv = self._connect(callback)
        
        return rcv


    def _connect(self, callback):
        self.connecting = True
        # Connect to Hexapod Server
        try:
            self.tcpipObj_Hexapod_1.connect((self.IP, self.port_1))
            self.tcpipObj_Hexapod_2.connect((self.IP, self.port_2))

            self.tcpipObj_Hexapod_1.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            self.tcpipObj_Hexapod_2.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            self.connection_status = True
            self.connecting = False
            rcv = f'Hexapod Connection Successful: | IP: {self.IP} | Port1: {self.port_1} | Port2: {self.port_2}'
            callback(rcv)

            # Autmoatically move to default position after successful connection
            self.move_to_default_position()

            return rcv
        
        except Exception as e:
            self.connection_status = False
            self.connecting = False
            rcv = f'Hexapod Connection Failed: {e}'
            callback(rcv)
            return rcv


    def clear_socket_buffer(self, sock):
        sock.setblocking(0)  # Set non-blocking mode
        try:
            while sock.recv(1024):  # Read and discard data
                print(f'clearing buffer: ({sock.recv(1024)})')
                pass
        except BlockingIOError:
            pass
        finally:
            sock.setblocking(1)  # Set back to blocking mode

    def send_command(self, command, timeout = 5):
        # Send command to TCP/IP server
        # Use tcpipObj_Hexapod_1 for regular commands, tcpipObj_Hexapod_2 as emergency stop

        if not self.connection_status:
            rcv = 'Hexpod not connected to server'
            return rcv
        
        # Discard unwanted server responses
        self.clear_socket_buffer(self.tcpipObj_Hexapod_1) 
        self.clear_socket_buffer(self.tcpipObj_Hexapod_2)


        try:
            command_with_newline = command + '\n' # add newline character to command

            if command == 'stop':
                self.tcpipObj_Hexapod_2.send(command_with_newline.encode())
                rcv = b''
                while not rcv:
                    rcv = self.tcpipObj_Hexapod_2.recv(1024) # Reads the response from the TCP/IP server
                
                rcv = rcv.decode()
                return rcv

            else:
                self.tcpipObj_Hexapod_1.send(command_with_newline.encode()) # Encodes the command string to bytestring UTF-8
                #print(f'command sent: {command}')
                rcv = b''
                start_time = time.time()
                while not rcv:
                    if time.time() - start_time > timeout:
                        rcv = 'Timeout'
                        print('Timeout')
                        return rcv
                    
                    #print('waiting for response')
                    rcv = self.tcpipObj_Hexapod_1.recv(1024) # Reads the response from the TCP/IP server
                
                #print('response received')
                rcv = rcv.decode()
        except Exception as e:
            rcv = f'Error: {e}'

        return rcv

    def move(self, pos, flag = "relative"):
        
        if self.connection_status is False:
            
            pos_current = self.position # use simulated position for testing

            if flag == "relative": # relative movement
                pos_new = [curr + p for curr, p in zip(pos_current, pos)] # add relative movement to current position for each coordinate
            elif flag == "absolute": # absolute movement
                pos_new = pos   
            
            self.position = pos_new # update fake position attribute

            rcv = 'Hexpod not connected to server'
            return rcv
        else:
            # Send command to get current position
            rcv = self.send_command('get_pos')
            #print(f'rcv: {rcv}')
            if rcv == 'Timeout':
                return rcv

            pos_current = list(map(float, rcv.split()))[1:] # remove first element which is the command
            #print(f'Current Position: {pos_current}')
            if flag == "relative": # relative movement
                pos_new = [curr + float(p) for curr, p in zip(pos_current, pos)] # add relative movement to current position for each coordinate
            elif flag == "absolute": # absolute movement
                pos_new = pos
            else:
                rcv = 'Incorrect input for flag'
                return rcv

            # Send command to set new position
            command = f'set_pos {" ".join(map(str, pos_new))}'
            rcv = self.send_command(command)
            if rcv == 'Timeout':
                return rcv 
            self.position = pos_new # update position attribute
            rcv += f": {self.position}" # add actual position to returned message
            return rcv

    def set_velocity(self, velocity):
        if not self.connection_status:
            rcv= 'Hexpod not connected to server'
            return rcv
        
        self.velocity = velocity
        rcv = self.send_command(f'set_vel {velocity}')
        if rcv == 'Timeout':
            return rcv
        return rcv

    def __repr__(self):
        return f"Hexapod(\nposition={self.position}\nTravelRanges={self.travel_ranges} \nIP={self.IP} \nPort1={self.port_1} \nPort2={self.port_2}\n)"
    

if __name__ == "__main__":
    hexapod = Hexapod()
    

    print("connect: "+ str(hexapod.connect_sockets()))    
    print("move: " + str(hexapod.move([1, 1, 1, 0, 0, 0], flag = "relative")))
    print("get_pos:" + str(hexapod.send_command("get_pos")))
    """
    print(hexapod.move_to_default_position())
    print(hexapod.send_command("get_pos"))
    

    print(hexapod.send_command("disconnect"))
    """