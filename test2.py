import serial
import time

# UART instellingen voor Raspberry Pi
UART_PORT = "/dev/serial0"  # GPIO14 (TX) en GPIO15 (RX)
BAUDRATE = 19200  # Standaardwaarde, wordt aangepast na detectie

def test_baudrates(baud_list):
    """Test een lijst van baudrates en retourneer de eerste die werkt."""
    for baud in baud_list:
        try:
            with serial.Serial(UART_PORT, baud, timeout=2) as ser:
                ser.write(b"AT\r\n")
                time.sleep(0.5)
                response = ser.read(ser.in_waiting).decode(errors='ignore').strip()
                if "OK" in response:
                    print(f"✅ Werkende baudrate gevonden: {baud}")
                    return baud
                else:
                    print(f"❌ Geen antwoord bij {baud}")
        except Exception as e:
            print(f"Fout bij {baud}: {e}")
    return None

def send_at_command(command, baudrate, timeout=2):
    """Stuur AT-commando naar modem en lees antwoord."""
    with serial.Serial(UART_PORT, baudrate, timeout=timeout) as ser:
        ser.write((command + "\r\n").encode())
        time.sleep(0.5)
        response = ser.read(ser.in_waiting).decode(errors='ignore')
        return response.strip()

if __name__ == "__main__":
    # Stap 1: Test verschillende baudrates
    mogelijke_baudrates = [9600, 19200, 57600, 115200]
    werkende_baud = test_baudrates(mogelijke_baudrates)

    if werkende_baud:
        # Stap 2: Gebruik de gevonden baudrate
        print("Stuur AT...")
        response = send_at_command("AT", werkende_baud)
        print("Antwoord:", response)

        # Voorbeeld: Lees IMEI
        imei = send_at_command("AT+CGSN", werkende_baud)
        print("IMEI:", imei)
    else:
        print("Geen werkende baudrate gevonden!")
