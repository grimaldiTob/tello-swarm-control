from djitellopy import Tello
import threading 
import socket
import sys

wifi_ssid = "mobirec"
wifi_password = "fa1vbw809e"
host = ''
port = 9000
locaddr = (host,port) 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.16.112', 8889)

sock.bind(locaddr)

def recv():
    while True: 
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break


print ('\r\n\r\nTello Python3 Demo.\r\n')

print ('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')

print ('end -- quit demo.\r\n')

recvThread = threading.Thread(target=recv)
recvThread.start()

while True: 

    try:
        msg = input("");

        if not msg:
            break  

        if 'end' in msg:
            print ('...')
            sock.close() 
            sys.exit() 
            break

        msg = msg.encode(encoding="utf-8") 
        sent = sock.sendto(msg, tello_address)
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()  
        break

def connect_to_wifi():
    try:
        tello = Tello()
        tello.connect()

        print(f"➤ Connessione alla rete Wi-Fi: {wifi_ssid}...")
        tello.send_control_command(f"ap {wifi_ssid} {wifi_password}")
        tello.end()
    except Exception as e:
        print("Errore")
