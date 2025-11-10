import serial
import time

PORT = "/dev/serial0"
BAUDRATE = 38400

ser = serial.Serial(PORT, BAUDRATE, timeout=2)
print(f"Poort {PORT} geopend op {BAUDRATE} baud.")

try:
    while True:
        cmd = input("Voer een commando in (bijv. AT): ")
        if cmd.lower() == "exit":
            break

        ser.write((cmd + "\r\n").encode('utf-8'))
        ser.flush()

        # Wacht tot antwoord binnenkomt
        response = b""
        start = time.time()
        while time.time() - start < 3:  # max 3 sec
            if ser.in_waiting:
                response += ser.read(ser.in_waiting)
            time.sleep(0.1)

        if response:
            print(f"Antwoord: {response.decode('utf-8', errors='ignore')}")
        else:
            print("Geen antwoord ontvangen.")

except Exception as e:
    print(f"Fout: {e}")
finally:
    ser.close()
