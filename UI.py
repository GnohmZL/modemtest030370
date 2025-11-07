import time
import serial
import logging
from colorama import init, Fore, Style

# Init colorama
init(autoreset=True)

# UART configuratie met baudrate 38400
uart = serial.Serial("/dev/serial0", baudrate=38400, timeout=2)

APN = "internet"
PINGIP = "8.8.8.8"

def log_step(step_name, success):
    symbol = "✅" if success else "❌"
    color = Fore.GREEN if success else Fore.RED
    print(f"{color}{symbol} {step_name}")

def send_at_command(command, expected="OK", delay=1, retries=3):
    """Stuur AT-commando en controleer op verwacht antwoord."""
    for attempt in range(retries):
        uart.reset_input_buffer()
        uart.reset_output_buffer()
        print(f"{Fore.CYAN}→ Verstuurd: {command}")
        uart.write((command + "\r\n").encode())
        time.sleep(delay)
        response = read_response(timeout=3)
        for line in response.strip().splitlines():
            print(f"{Fore.YELLOW}← Antwoord: {line.strip()}")
        if expected in response:
            return True
        print(f"{Fore.MAGENTA}↻ Retry {attempt+1}/{retries} voor {command}")
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
    command = "AT+CSQ"
    print(f"{Fore.CYAN}→ Verstuurd: {command}")
    uart.write((command + "\r\n").encode())
    time.sleep(1)
    resp = read_response()
    for line in resp.strip().splitlines():
        print(f"{Fore.YELLOW}← Antwoord: {line.strip()}")
        if "+CSQ:" in line:
            try:
                rssi = int(line.split(":")[1].split(",")[0].strip())
                if rssi == 99:
                    print(f"{Fore.RED}❌ Signaalsterkte onbekend")
                else:
                    dbm = -113 + (rssi * 2)
                    print(f"{Fore.GREEN}✅ Signaalsterkte: {rssi} → ongeveer {dbm} dBm")
            except Exception as e:
                print(f"{Fore.RED}❌ Fout bij verwerken signaalsterkte: {e}")
    return resp

def get_ip_address():
    """Vraag IP-adres op via AT+CGPADDR."""
    command = "AT+CGPADDR=1"
    print(f"{Fore.CYAN}→ Verstuurd: {command}")
    uart.write((command + "\r\n").encode())
    time.sleep(1)
    resp = read_response()
    for line in resp.strip().splitlines():
        print(f"{Fore.YELLOW}← Antwoord: {line.strip()}")
        if "+CGPADDR:" in line:
            ip = line.split(",")[-1].strip()
            print(f"{Fore.GREEN}✅ IP-adres: {ip}")
    return resp

def check_network_registration():
    """Controleer of modem geregistreerd is op netwerk (normaal of roaming)."""
    command = "AT+CREG?"
    print(f"{Fore.CYAN}→ Verstuurd: {command}")
    uart.write((command + "\r\n").encode())
    time.sleep(1)
    resp = read_response()
    for line in resp.strip().splitlines():
        print(f"{Fore.YELLOW}← Antwoord: {line.strip()}")
        if "+CREG:" in line and ("0,1" in line or "0,5" in line):
            return True
    return False

def activate_network():
    """Activeer netwerkverbinding via CGATT en CGACT."""
    success1 = send_at_command("AT+CGATT=1")
    log_step("Netwerkverbinding activeren (CGATT)", success1)
    if not success1:
        return False
    success2 = send_at_command("AT+CGACT=1,1")
    log_step("PDP-context activeren (CGACT)", success2)
    return success2

def main():
    print(f"{Style.BRIGHT}📡 Start uitgebreide netwerk test...\n")

    log_step("Modem check", send_at_command("AT"))
    log_step("SIM status", send_at_command("AT+CPIN?", "READY"))
    log_step("Netwerkregistratie", check_network_registration())
    check_signal_strength()
    log_step("APN instellen", send_at_command(f'AT+CGDCONT=1,"IP","{APN}"'))
    log_step("Netwerk activeren", activate_network())
    get_ip_address()

    # Ping uitvoeren
    ping_success = send_at_command(f'AT+PING="{PINGIP}"', "OK", delay=5)
    log_step(f"Ping naar {PINGIP}", ping_success)

if __name__ == "__main__":
    main()
