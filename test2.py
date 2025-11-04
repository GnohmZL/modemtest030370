import serial
import time

# UART instellingen voor Raspberry Pi
UART_PORT = "/dev/serial0"  # GPIO14 (TX) en GPIO15 (RX)
BAUDRATE = 115200

def send_at_command(command, timeout=2):
    """Stuur AT-commando naar modem en lees antwoord."""
    with serial.Serial(UART_PORT, BAUDRATE, timeout=timeout) as ser:
        ser.write((command + "\r\n").encode())
        time.sleep(0.5)
        response = ser.read(ser.in_waiting).decode(errors='ignore')
        return response.strip()

if __name__ == "__main__":
    # Test AT-commando
    print("Stuur AT...")
    response = send_at_command("AT")
    print("Antwoord:", response)

    # Voorbeeld: Lees IMEI
    imei = send_at_command("AT+CGSN")
    print("IMEI:", imei)
