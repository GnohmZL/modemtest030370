import serial
import time

# Open seriële verbinding
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=5)

# Zet modem in tekstmodus
ser.write(b'AT+CMGF=1\r')
time.sleep(1)
print(ser.read_all().decode())

# Verstuur SMS
ser.write(b'AT+CMGS="+31612345678"\r')
time.sleep(2)  # wacht op > prompt

# Verstuur bericht + Ctrl+Z
message = "Hallo, dit is een testbericht"
ser.write((message + '\x1A').encode())  # \x1A is Ctrl+Z
time.sleep(5)

# Lees antwoord
response = ser.read_all().decode(errors='ignore')
print(response)

ser.close()
