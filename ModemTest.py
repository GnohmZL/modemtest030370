import serial
import time

# ANSI-kleuren
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Seriële poortinstellingen
SERIAL_PORT = "/dev/ttyUSB0"  # Pas aan indien nodig
BAUDRATE = 38400
TIMEOUT = 2

# Uitgebreide lijst van AT-commando's
at_commands = {
    "Modem communicatie test": "AT",
    "SIM status": "AT+CPIN?",
    "Signaalsterkte (CSQ)": "AT+CSQ",
    "Netwerk registratie (CREG)": "AT+CREG?",
    "Netwerk registratie (CEREG)": "AT+CEREG?",
    "GPRS status": "AT+CGATT?",
    "Operator selectie": "AT+COPS?",
    "Netwerkinformatie": "AT+QNWINFO",
    "Signaalinformatie (QCSQ)": "AT+QCSQ",
    "APN-profielen": "AT+CGDCONT?",
    "PDP context status": "AT+CGACT?",
    "ICCID (eSIM)": "AT+CCID",
    "IMSI": "AT+CIMI",
    "Voorkeursnetwerken": "AT+CPOL",
    "SIM status (QSIMSTAT)": "AT+QSIMSTAT?",
    "IMEI nummer": "AT+CGSN",
    "Serving cell info": "AT+QENG=\"servingcell\"",
    "PDP configuratie": "AT+QICSGP",
    "PDP activeren": "AT+QIACT",
    "Socket openen": "AT+QIOPEN",
    "Data verzenden": "AT+QISEND",
    "Socket sluiten": "AT+QICLOSE"
}

# Resultaten opslaan
results = {}

# Functie om AT-commando te sturen en antwoord te verwerken
def send_at_command(ser, command):
    print(f"{CYAN}>>> Verstuur commando: {command}{RESET}")
    ser.write((command + "\r").encode())
    time.sleep(0.7)
    response = ser.read_all().decode(errors='ignore').strip()
    print(f"{YELLOW}<<< Response:\n{response}{RESET}\n")
    return response

# Seriële communicatie starten
try:
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT) as ser:
        print(f"{GREEN}Verbonden met {SERIAL_PORT} op {BAUDRATE} bps{RESET}\n")
        for description, command in at_commands.items():
            print(f"{CYAN}--- {description} ---{RESET}")
            response = send_at_command(ser, command)
            success = "OK" in response and "ERROR" not in response
            results[description] = {
                "Commando": command,
                "Resultaat": response,
                "Status": f"{GREEN}Succes{RESET}" if success else f"{RED}❌ Fout{RESET}"
            }

    # Eindrapport
    print(f"\n{CYAN}================== SAMENVATTING =================={RESET}")
    all_success = True
    for desc, info in results.items():
        print(f"{desc}: {info['Status']}")
        print(f"  {CYAN}Commando:{RESET} {info['Commando']}")
        print(f"  {YELLOW}Resultaat:{RESET} {info['Resultaat']}\n")
        if "❌" in info["Status"]:
            all_success = False

    if all_success:
        print(f"{GREEN}Alle tests zijn succesvol uitgevoerd.{RESET}")
    else:
        print(f"{RED}Eén of meerdere tests zijn mislukt. Zie details hierboven.{RESET}")

except serial.SerialException as e:
    print(f"{RED}Fout bij openen van seriële poort: {e}{RESET}")
except Exception as e:
    print(f"{RED}Onverwachte fout: {e}{RESET}")
