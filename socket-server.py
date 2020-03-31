#!/usr/bin/env python3

##############################################################################
# Socket Server on raspberry pi with current measure shield
##############################################################################

# this python script runs on a Raspberry pi with a current measure shield
# and connets to a pi with TWCManager BitterAndReal fork

# It measures how many amps are drawn at the utility mains to protect the main fuse of your house.
# And we can use the mains reading to calculate how much green energy we have left to charge the car.

# Serial Output of the current measure print:
    # NodeID Realpower1 ApparentPower1 Irms1 Vrms1 PowerFactor1 Realpower2 ApparentPower2 Irms2 Vrms2 PowerFactor2 Realpower3 ApparentPower3 Irms3 Vrms3 PowerFactor3

    # >> serial message split into a list:
    # mains[0] AC board NodeID
    # mains[1] RealPower L1
    # mains[2] ApparentPower L1
    # >>> mains[3] Irms L1
    # mains[4] Vrms L1
    # mains[5] PowerFactor L1
    # mains[6] RealPower L2
    # mains[7] ApparentPower L2
    # >>> mains[8] Irms L2
    # mains[9] Vrms L2
    # mains[10] PowerFactor L2
    # mains[11] RealPower L3
    # mains[12] ApparentPower L3
    # >>> mains[13] Irms L3
    # mains[14] Vrms L3
    # mains[15] PowerFactor L3


import serial
import socket
import time
import threading

debugLevel = 0

#HOST = '192.168.0.66' # Client adres???
HOST = ''              # listening to all ports
PORT = 65432           # Port to listen on (non-privileged ports are > 1023)


def time_now():
    return(datetime.now().strftime("%H:%M:%S"))

def read_serial():
    global message_to_send, line_time, SerialReadErrorInRow, SerialReadErrorCount

    ser = serial.Serial(
      port='/dev/serial0',
      baudrate = 38400
#      , timeout=2
    )

    while True: # loop forever
        line = ser.readline()
        mains = line[:-2].decode().split(" ")
        if(debugLevel >= 3):
            print("Serial line: " + str(line))

        if(len(mains) >= 16):
            message_to_send = line
            line_time = time.time()
            SerialReadErrorInRow = 0

            if(debugLevel >= 2):
                print(" L1:" + str(mains[3]) +
                    "  L2:" + str(mains[8]) +
                    "  L3:" + str(mains[13]))

        else:
            SerialReadErrorCount += 1
            SerialReadErrorInRow += 1
            print(time_now() + "ERROR: could not read serial line (" +
                str(SerialReadErrorInRow) + "x in row,  " +
                str(SerialReadErrorCount) + " total)")
            # if last valid serial reading is older than 5 sec send error
            if(time.time() - line_time > 5):
                message_to_send = b'ERROR'
                print(time_now() + "message_to_send = ERROR (" +
                    str(int(time.time() - line_time)) + " sec no reading)")

def socket_server():
    global message_to_send, line_time

    while True: # loop forever

        time.sleep(0.2)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            if(debugLevel >= 2):
                print("listening on port " + str(PORT))

            conn, addr = s.accept()

            with conn:
                if(debugLevel >= 2):
                    print('Connected by', addr)
                while True:
                    data = conn.recv(8)
                    if not data:
                        break
                    conn.sendall(message_to_send)
                    if(debugLevel >= 1):
                        print("serial line sent")

########################
# main thread
########################
message_to_send = b'hello'
line_time = 0
SerialReadErrorInRow = 0
SerialReadErrorCount = 0

# create two threads
sr = threading.Thread(target=read_serial)
ss = threading.Thread(target=socket_server)

sr.start()
ss.start()

print (time_now() + "read_serial & socket_server started")

while 1:
    time.sleep(1)
    if(sr.isAlive() == False):
        sr.start()
        print (time_now() + "read_serial restarted!")
    if(ss.isAlive() == False):
        ss.start()
        print (time_now() + "socket_server restarted!")
