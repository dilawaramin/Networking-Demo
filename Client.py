# Networking Class Demonstration
# Note: Launch server file first

# Import socket module
from socket import * 
from struct import *
import random
import time
import sys # In order to terminate the program
#### PROFESSORS SERVER INFO ####
### Server IP address: 34.67.93.93
### Server port number : 12000 


#### PROFS DEBUGGING ####
def check_server_response(response):
    data_len, pcode, entity = unpack_from('!IHH', response)
    if pcode == 555:
        response = response[8:]
        print(response.decode())
        sys.exit()
    return


### PHASE A ###


print("--------------PHASE A--------------\n") 
serverName = 'localhost'
# serverName = '10.84.88.53'
# profs server:
#serverName = '34.67.93.93'
# Assign a port number
serverPort = 12000

# Bind the socket to server address and server port
clientSocket = socket(AF_INET, SOCK_DGRAM)

# initialize values
data = b"Hello World!!!"
# pad the length
while len(data) % 4 != 0:
    data = data + bytearray(1)
data_length = len(data)
entity = 1
pcode = 0

# create packet (?)
packet = pack(f'!IHH{data_length}s', data_length, pcode, entity, data)

#clientSocket.connect((serverName, serverPort))
clientSocket.sendto( packet, (serverName, serverPort))
newPacket, serverAddress = clientSocket.recvfrom(2048)
# unpack recieved data
data_length, pcode, entity, repeat, upd_port, leng, codeA = unpack("!IHHIIHH", newPacket[:20])
# close socket, to re bind to new one
clientSocket.close()
print(f"""Recieved from server: 
      
Length: {data_length}
pcode:  {pcode}
entity: {entity}
repeat: {repeat}
UDP:    {upd_port}
len:    {leng}
codeA:  {codeA}""")
print("\n----------PHASE A COMPLETE----------\n\n")


### PHASE B ###


print("\n--------------PHASE B--------------\n") 
# open new socket object
clientSocket = socket(AF_INET, SOCK_DGRAM)
# Initialize repeat id
rep = 0
# set the timer for socket to receive acknowledgements
clientSocket.settimeout(5)
# Iterate till repeat to send repeats
for i in range(0, repeat):
    # initialize values
    pcode = codeA
    entity = 1
    packetID = rep
    data = b'0' * leng
    # ensure data is divisble by 4
    while len(data) % 4 != 0:
        data = data + bytearray(1)
    # length of data and packetID (remember to subtract 4 when unpacking)
    data_length = len(data) + 4 
    # pack the packet
    pbPacket = pack(f'!IHHI{len(data)}s', data_length, pcode, entity, packetID, data)
    # send to new server
    while True:
        try:
            # Send the packet to the server
            clientSocket.sendto(pbPacket, (serverName, upd_port))
            # wait for acknowledgement
            ackn, serverAddress = clientSocket.recvfrom(2048)
            # Unpack the acknowledgment
            data_length, pcode, entity, acked_packet_id = unpack('!IHHI', ackn)
            # Print acknowledgment
            print(f"Acknowledgment received with ID: {acked_packet_id}\n")
            if acked_packet_id == packetID:
                break  # Exit the acknowledgment loop when the expected acknowledgment is received
        except timeout:
                # If the expected acknowledgment is not received within 5 seconds, resend the packet
                print("No acknowledgment received. Resending the packet...\n")
                continue

        break  # Exit the packet retransmission loop when the acknowledgment is received
    rep += 1
    continue 
# now wait for the TCP info (PHASE B-2)
b2packet, serverAddress = clientSocket.recvfrom(2048)
data_length, pcode, entity, tcp_port, codeB = unpack('!IHHII', b2packet)
#end of phase b
print(f"PHASE B-2 Values: DL:{data_length}, Pcode:{pcode}, ent:{entity}, TCP:{tcp_port}, codeB:{codeB}")
print("\n----------PHASE B COMPLETE----------\n\n")


### PHASE C ###


print("\n--------------PHASE C--------------\n")
# wait for the server to first connect to socket/port
time.sleep(5)
# Create socket
clientSocket = socket(AF_INET, SOCK_STREAM)
print("client ready to connect...\n")
# Connect the socket to server address and port (?)
clientSocket.connect((serverName, tcp_port))
print("client ready to receive...\n")
# recieve the repeat2 packet from server
cpacket = clientSocket.recv(1024)
# unpack the packet
data_length, pcode, entity, repeat2, len2, codeC, char = unpack("!IHHIIIc", cpacket)
# decode the char
char = char.decode('ascii')
# print the receieved data
print(f"Successfully received new data.")
print("\n----------PHASE C COMPLETE----------\n\n")


### PHASE D ###


print("\n--------------PHASE D--------------\n")
# Initialize repeat packet values 
pcode = codeC
entity = 1
data = bytes(char, 'UTF-8') * len2
# debugging
print(f"Length of data (before padding): {len(data)}")
# pad the data
while len(data) % 4 != 0:
    data = data + bytearray(1)
data_length = len(data)
# debugging
print(f"Data Length: {data_length}")
print(f"Entity: {entity}")
print(f"Expected number of packets to send: {repeat2}\n")
# pack the packet !
dpacket = pack(f"!IHH{data_length}s", data_length, pcode, entity, data)
# send the packet repeat2 amount of times
for i in range(0, repeat2):
    time.sleep(1) # short delay to prevent overflow
    clientSocket.send(dpacket)
    print(f"Successfully sent packet number: {i + 1}\n")
    
# Receive the final packet
print("Ready to receive...")
finalPacket = clientSocket.recv(1024)
# unpack the final packet
data_length, pcode, entity, codeD = unpack("!IHHI", finalPacket)
print(f"""Final packet recevied:\n
Data Length: {data_length}
pcode:       {pcode}
entity:      {entity}
codeD:       {codeD}""")

print("\n----------PHASE D COMPLETE----------\n\n")


print("Preparing to shutdown client. Goodbye!\n")


print("\nEND OF PROGRAM")
sys.exit()#Terminate the program after sending the corresponding data