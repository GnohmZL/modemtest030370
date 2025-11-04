import serial
import smbus
import time

# I2C instellingen voor CJMCU-0108
I2C_BUS = 1
MUX_ADDR = 0x70  # Standaard adres van TCA9548A (CJMCU-0108)
bus = smbus.SMBus(I2C_BUS)

def select_channel(channel):
    """Selecteer UART-kanaal via I2C multiplexer (0-7)."""
    if channel < 0 or channel > 7:
        raise ValueError("Kanaal moet tussen 0 en 7 liggen.")
    bus.write_byte(MUX_ADDR, 1 << channel)
    print(f"I2C: Kanaal {channel} geselecteerd.")

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
    # Selecteer het juiste kanaal op CJMCU-0108
    select_channel(0)  # Stel in op het kanaal waar je modem zit

    # Test AT-commando
    print("Stuur AT...")
    response = send_at_command("AT")
    print("Antwoord:", response)

    # Voorbeeld: Lees IMEI
    imei = send_at_command("AT+CGSN")
    print("IMEI:", imei)
