import time
import serial
import logging

# Logging configuratie
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# UART configuratie
uart = serial.Serial("/dev/serial0", baudrate=115200, timeout=2)

APN = ""

def send_at_command(command, expected="OK", delay=1, retries=3):
    """Stuur AT-commando en controleer op verwacht antwoord."""
    for attempt in range(retries):
        uart.reset_input_buffer()
        uart.reset_output_buffer()
        uart.write((command + "\r\n").encode())
        time.sleep(delay)
        response = read_response(timeout=3)
        logging.info(f"CMD: {command} | RESP: {response.strip()}")
        if expected in response:
            return True
        logging.warning(f"Retry {attempt+1}/{retries} voor {command}")
    return False

def read_response(timeout=2):
    """Lees respons met timeout."""
    end_time = time.time() + timeout
    response = b""
    while time.time() < end_time:
        if uart.in_waiting:
            response += uart.read(uart.in_waiting)
        time.sleep(0.1)
    return response.decode(errors='ignore')

def check_signal_strength():
    """Controleer signaalsterkte via AT+CSQ."""
    uart.write(b"AT+CSQ\r\n")
    time.sleep(1)
    resp = read_response()
    logging.info(f"Signaalsterkte: {resp.strip()}")
    return resp

def get_ip_address():
    """Vraag IP-adres op via AT+CGPADDR."""
    uart.write(b"AT+CGPADDR=1\r\n")
    time.sleep(1)
    resp = read_response()
    logging.info(f"IP-adres: {resp.strip()}")
    return resp

def main():
    logging.info("Start uitgebreide netwerk test...")

    # 1. Modem check
    if not send_at_command("AT"):
        logging.error("Modem reageert niet.")
        return

    # 2. SIM status
    if not send_at_command("AT+CPIN?", "READY"):
        logging.error("SIM niet klaar.")
        return

    # 3. Netwerkregistratie (normaal of roaming)
    if not send_at_command("AT+CREG?", "0,1") and not send_at_command("AT+CREG?", "0,5"):
        logging.error("Niet geregistreerd op netwerk.")
        return

    # 4. Signaalsterkte
    check_signal_strength()

    # 5. APN instellen
    if not send_at_command(f'AT+CGDCONT=1,"IP","{APN}"'):
        logging.error("APN instellen mislukt.")
        return

    # 6. PDP-context activeren
    if not send_at_command("AT+CGACT=1,1"):
        logging.error("PDP-context activeren mislukt.")
        return

    # 7. IP-adres ophalen
    get_ip_address()

    # 8. Ping naar Google DNS
    if send_at_command('AT+PING="8.8.8.8"', "OK", delay=5):
        logging.info("Ping succesvol! Netwerk werkt.")
    else:
        logging.error("Ping mislukt.")

if __name__ == "__main__":
    main()
