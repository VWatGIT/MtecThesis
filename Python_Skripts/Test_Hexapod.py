import socket
import time

def move_hex(hex_obj, flag, pos):
    # Send command to get current position
    hex_obj.write(b'get_pos\n')
    rcv = b''
    while not rcv:
        rcv = hex_obj.read()
    pos_curr = list(map(float, rcv.decode().split()))[1:] # remove first element which is the command

    if flag == 1: # relative movement
        pos_act = [curr + p for curr, p in zip(pos_curr, pos)]
    elif flag == 2: # absolute movement
        pos_act = pos
    else:
        print('option not implemented!')
        return None, None

    # Send command to set new position
    hex_obj.write(f'set_pos {" ".join(map(str, pos_act))}\n'.encode())
    rcv = b''
    while not rcv:
        rcv = hex_obj.read()

    res = rcv.decode()
    return res, pos_act

def query_tcpip(tcpipObj, command):
    tcpipObj.write(command.encode()) # Encodes the command string to bytestring UTF-8
    rcv = b''
    while not rcv:
        rcv = tcpipObj.read() # Reads the response from the TCP/IP server
    
    return rcv.decode()

# Define Addresses
IP_Hexapod = '134.28.45.71'
port_Hexapod_1 = 5464
port_Hexapod_2 = 5465

# Connect to Hexapod
# Socket 1 for commands
tcpipObj_Hexapod_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpipObj_Hexapod_1.connect((IP_Hexapod, port_Hexapod_1))

# Socket 2 for emergency stop
tcpipObj_Hexapod_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpipObj_Hexapod_2.connect((IP_Hexapod, port_Hexapod_2))

# Command Dictionary
commands = {
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

# Test Commands

# Get Current Pose
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['get_pos'])
print(rcv)

# Below are example commands that can be executed. Uncomment to test them.
"""
# Set Sub Folder
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['set_sub_folder'])
print(rcv)

# Set Local Filename
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['set_local_file_name'])
print(rcv)

# Start and Stop RTLocal
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['start_rt_local'])
print(rcv)
time.sleep(1)
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['stop_rt_local'])
print(rcv)

# Set Velocity
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['set_vel'])
print(rcv)

# Drive Absolute Position
abs_position = [0, 0, -3.1, 0, 0, 0] # [x, y, z, roll, pitch, yaw]
res, pos_latest_init = move_hex(tcpipObj_Hexapod_1, 2, abs_position)

# Drive Relative Position
rel_position = [0, 0, 0, 0, 0, 0]
res, pos_latest_init = move_hex(tcpipObj_Hexapod_1, 1, rel_position)

# Disconnect
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['disconnect'])
print(rcv)

# Quit
rcv = query_tcpip(tcpipObj_Hexapod_1, commands['quit'])
print(rcv)

# Emergency Stop
rcv = query_tcpip(tcpipObj_Hexapod_2, commands['stop'])
print(rcv)
"""
# Close sockets
tcpipObj_Hexapod_1.close()
tcpipObj_Hexapod_2.close()
