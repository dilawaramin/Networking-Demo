# Networking demonstration

# Import socket module
from socket import * 
import struct
import random
import time
import string
import sys # In order to terminate the program

# Assign a port number
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)

### PHASE A ###

print("--------------PHASE A--------------\n") 
# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))

# set a timeout for 3 seconds
serverSocket.settimeout(3)
# use try except block for timers
try:
	while True:

		print('The server is ready to receive...')
		packet, clientAddress = serverSocket.recvfrom(1024)
		# unpack the packet header, to determine length of data
		data_length, pcode, entity = struct.unpack('!IHH', packet[:8])
		# decode/unpack data using data_length
		data = packet[8:8 + data_length].decode()
	
		# validate the packet
		if len(packet) % 4 != 0:
			serverSocket.close()
			print("Indivisible packet length")
			break
			
		# validate data
		if data_length != len(data)  or entity != 1 or pcode != 0:
			serverSocket.close()
			print("Incorrect data")
			break
			
		print(data)
		
		# update the data before sending back
		pcode = 0 # still no change according to assignment instructions
		entity = 2
		repeat = random.randint(5, 20)
		upd_port = random.randint(20000, 30000)
		leng = random.randint(50, 100)
		codeA = random.randint(100, 400)
		# create a new updated packet
		newPacket = struct.pack("!IHHIIHH", data_length, pcode, entity, repeat, upd_port, leng, codeA)
		# send the new packet
		serverSocket.sendto(newPacket, clientAddress)
		print("Packet successfully sent!")
		break
# Raise exception
except socket.timeout:
    print("Timeout: No data received within the specified time.")
# finally what happens
finally:
    serverSocket.close()
    

# close this server, and bing to the new port
serverSocket.close()  
# new bind port
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", upd_port))
print("\n----------PHASE A COMPLETE----------\n\n")


### PHASE B ###


print("\n--------------PHASE B--------------\n")
# set the repeat counter
rep = 0
# random test staller
counter = 0
# commence
while True:

	print('The server is ready to receive...')
	bPacket, clientAddress = serverSocket.recvfrom(1024)
	# unpack the packet for scanning
	data_length, pcode, entity, packetID = struct.unpack('!IHHI', bPacket[:12])
	# decode/unpack data using data_length
	data = bPacket[12:].decode()
	# print what was received
	print(f"Successfully received packet with iD: {packetID}\n")
	# begin validating
	if (data_length - 4) != len(data) or packetID != rep:
		serverSocket.close()
		print("Incorrect data (len or ID or order)")
		break
	# create acknowledgement packet
	pcode = codeA
	entity = 2
	acked_packet_id = rep
	data_length = 4 # since the data is only acked packet id and it is an integer
	# PACK THE PACKET
	ackn = struct.pack('!IHHI', data_length, pcode, entity, acked_packet_id)
	# UNCOMMENT THIS TO TEST THE RESENDING OF PACKETS FROM CLIENT SIDE. tag: debuggign
	# # random timer in code to test client
	# if rep == 3 and counter < 3:
	# 	time.sleep(5)
	# 	print(f"counter: {counter}")
	# 	counter += 1
	# 	continue
	# send the acknowledegment
	serverSocket.sendto(ackn, clientAddress)
	rep += 1
	if rep == repeat:
		break
# PHASE B-2 Packet send
pcode = codeA
entity = 2
tcp_port = random.randint(20000, 30000)
codeB = random.randint(100, 400)
data_length = 8
b2packet = struct.pack('!IHHII', data_length, pcode, entity, tcp_port, codeB)
serverSocket.sendto(b2packet, clientAddress)
print(f"Updated port info sent to client. Server will change ports shortly!")
### end of phase b
print("\n----------PHASE B COMPLETE----------\n\n")


### PHASE C ###


print("\n--------------PHASE C--------------\n")
# Create a new socket to listen to the TCP port sent above
serverSocket = socket(AF_INET, SOCK_STREAM)
# Bind to the TCP port
serverSocket.bind(("", tcp_port))
# Begin listening 
serverSocket.listen(1)
print ('The server is ready to receive')
# setup a connection with the client
connectionSocket, addr = serverSocket.accept()
# Initialize the values that will be in the packet
pcode = codeB
entity = 2
repeat2 = random.randint(5, 20)
len2 = random.randint(50, 100)
codeC = random.randint(100, 400)
char = random.choice(string.ascii_uppercase) # select a random upper case letter
data_length = 13
# print the data that is to be sent
print(f"""Recieved data: DL:  {data_length}
pcode:   {pcode}
entity:  {entity}
repeat2: {repeat2}
len2:    {len2}
codeC:   {codeC}
char:    {char}""")
# create the packet
cpacket = struct.pack('!IHHIIIc', data_length, pcode, entity, repeat2, len2, codeC, char.encode())
# send the packet
connectionSocket.send(cpacket)
print("\n----------PHASE C COMPLETE----------\n\n")


### PHASE D ###


print("\n--------------PHASE D--------------\n")
# debugging
print(f"Expecting to receive {repeat2} packets\n")
# begin receiving repeat packets
for i in range(0, repeat2):
    dpacket = connectionSocket.recv(1024)
    # unpack the recieved packet
    data_length, pcode, entityd = struct.unpack("!IHH", dpacket[:8])
    # unpack remaning data
    data = dpacket[8:].decode()
    # print success message
    print(f"Successfully recieved packet number: {i + 1}\n")

# prepare the final packet for send
pcode = codeC
entity = 2
codeD = random.randint(100, 400)
data_length = 4
print("Ready to send final packet...\n")
# pack the packet
finalPacket = struct.pack("!IHHI", data_length, pcode, entity, codeD)
connectionSocket.send(finalPacket)
print("Final packet successfully sent.")
print("\n----------PHASE D COMPLETE----------\n\n")

print(" Preparing to shutdown server. Goodbye!\n")


print("\nEND OF PROGRAM") # end of the program (self explanatory lol)
serverSocket.close()  
sys.exit() # Terminate the program after sending the corresponding data
