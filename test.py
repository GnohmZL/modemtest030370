import serial
import time

PORT = "/dev/serial0"   # of "/dev/ttyAMA0"
BAUDRATE = 115200       # pas aan indien nodig

# Open seriële poort
ser = serial.Serial(PORT, BAUDRATE, timeout=2)
print(f"Poort {PORT} geopend op {BAUDRATE} baud.")

try:
    while True:
        cmd = input("Voer een commando in (bijv. AT): ")
        if cmd.lower() == "exit":
            print("Script afgesloten.")
            break

        # Verstuur commando met CRLF
        ser.write((cmd + "\r\n").encode('utf-8'))
        time.sleep(0.5)

        # Lees antwoord
        response = ser.read(ser.in_waiting or 64)
        if response:
            print(f"Antwoord: {response.decode('utf-8', errors='ignore')}")
        else:
            print("Geen antwoord ontvangen.")

except Exception as e:
    print(f"Fout: {e}")
finally:
    ser.close()
