import time
import serial
import logging

# Logging configuratie
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# UART configuratie
uart = serial.Serial("/dev/serial0", baudrate=38400, timeout=2)

APN = "internet"  # Vul hier je APN in

def send_at_command(command, expected="OK", delay=1, retries=3):
    """Stuur AT-commando en controleer op verwacht antwoord."""
    for attempt in range(retries):
        uart.reset_input_buffer()
        uart.reset_output_buffer()
        uart.write((command + "\r\n").encode())
        time.sleep(delay)
        response = read_response(timeout=3)
        # Print elke regel apart
        for line in response.strip().splitlines():
            logging.info(f"RESP: {line.strip()}")
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
    """Controleer signaalsterkte via AT+CSQ en geef dBm waarde."""
    uart.write(b"AT+CSQ\r\n")
    time.sleep(1)
    resp = read_response()
    for line in resp.strip().splitlines():
        logging.info(f"RESP: {line.strip()}")
        if "+CSQ:" in line:
            try:
                rssi = int(line.split(":")[1].split(",")[0].strip())
                if rssi == 99:
                    logging.warning("Signaalsterkte onbekend of niet beschikbaar.")
                else:
                    # Omrekening naar dBm (ongeveer)
                    dbm = -113 + (rssi * 2)
                    logging.info(f"Signaalsterkte: {rssi} → ongeveer {dbm} dBm")
            except Exception as e:
                logging.error(f"Fout bij verwerken signaalsterkte: {e}")
    return resp

def get_ip_address():
    """Vraag IP-adres op via AT+CGPADDR."""
    uart.write(b"AT+CGPADDR=1\r\n")
    time.sleep(1)
    resp = read_response()
    for line in resp.strip().splitlines():
        logging.info(f"RESP: {line.strip()}")
        if "+CGPADDR:" in line:
            ip = line.split(",")[-1].strip()
            logging.info(f"Toegewezen IP-adres: {ip}")
    return resp

def check_network_registration():
    """Controleer of modem geregistreerd is op netwerk (normaal of roaming)."""
    uart.write(b"AT+CREG?\r\n")
    time.sleep(1)
    resp = read_response()
    for line in resp.strip().splitlines():
        logging.info(f"RESP: {line.strip()}")
        if "+CREG:" in line and ("0,1" in line or "0,5" in line):
            logging.info("Modem is succesvol geregistreerd op netwerk.")
            return True
    logging.warning("Modem is niet geregistreerd op netwerk.")
    return False

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

    # 3. Netwerkregistratie
    if not check_network_registration():
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
