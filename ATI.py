import serial
import time

PORT = "/dev/serial0"
BAUDRATE = 38400

# Open seriële poort met vaste configuratie
ser = serial.Serial(
    PORT,
    baudrate=BAUDRATE,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=3
)

print(f"Poort {PORT} geopend op {BAUDRATE} baud.")

try:
    while True:
        cmd = input("Voer een AT-commando in (bijv. ATI): ")
        if cmd.lower() == "exit":
            print("Script afgesloten.")
            break

        # Verstuur commando met CRLF
        ser.write((cmd + "\r\n").encode('utf-8'))
        ser.flush()

        # Lees antwoord
        response = b""
        start = time.time()
        while time.time() - start < 3:
            if ser.in_waiting:
                response += ser.read(ser.in_waiting)
            time.sleep(0.1)

        if response:
            print(f"Antwoord:\n{response.decode('utf-8', errors='ignore')}")
        else:
            print("Geen antwoord ontvangen.")

except Exception as e:
    print(f"Fout: {e}")
finally:
    ser.close()
