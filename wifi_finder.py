#!/bin/python

#░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓███████▓▒░  
#░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
#░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
#░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
#░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
#░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ 
#░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                                               
# Date created: 11/07/2024
# Last Revision: 11/07/2024

# Purpose: This script scans and outputs wifi networks near you
# run pip install -r requirements.txt to install all depedencies required

import subprocess,threading,re,time,sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Spinner animation
def spinner_animation(stop_event):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(Fore.YELLOW + f"\r{Style.BRIGHT}Scanning WiFi Networks... {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        time.sleep(0.1)
        idx += 1
    sys.stdout.write(Fore.GREEN + "\rScan complete!             \n")

# Signal Color strenght
def get_signal_color(signal_str):
    try:
        signal = int(signal_str)
        if signal < 25:
            return Fore.RED
        elif signal < 50:
            return Fore.YELLOW
        else:
            return Fore.GREEN
    except ValueError:
        return Fore.WHITE  # fallback in case signal is not an integer

def parse_nmcli_line(line):
    # Split on two or more spaces to separate columns
    parts = re.split(r'\s{2,}', line.strip())
    ssid = parts[0] if len(parts) > 0 else ""
    bssid = parts[1] if len(parts) > 1 else ""
    signal = parts[2].replace("%", "") if len(parts) > 2 else ""
    channel = parts[3] if len(parts) > 3 else ""
    security = parts[4] if len(parts) > 4 else ""

    if not ssid or ssid == "--":
        ssid = "(Hidden)"
    if not security:
        security = "--"

    return ssid, bssid, signal, channel, security

# Scanner
def scan_wifi_network():

    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner,))
    spinner_thread.start()

    try:
        # Run nmcli to list nearby Wi-Fi networks
        result = subprocess.run(['nmcli','--fields','SSID,BSSID,SIGNAL,CHAN,SECURITY','dev','wifi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    finally:
        # Stop the spinner regardless of what happens
        stop_spinner.set()
        spinner_thread.join()

    if result.returncode != 0:
        print(Fore.RED + "Error scanning wifi networks:")
        print(result.stderr)
        return

    lines = result.stdout.strip().split('\n')
    if not lines:
        print("No networks found.")
        return

    print(Fore.CYAN + "\n Nearby WI-FI Networks:\n" + Style.RESET_ALL)

    # Skip header line, start from second line
    for line in lines[1:]:
        if not line.strip():
            continue
        ssid, bssid, signal, channel, security = parse_nmcli_line(line)

        ssid_color = Fore.GREEN if ssid != "(Hidden)" else Fore.MAGENTA
        signal_color = get_signal_color(signal)
        security_color = Fore.RED if security == "--" else Fore.BLUE

        print(
            f"{ssid_color}SSID: {ssid:<25}"
            f"{Style.RESET_ALL} | {Fore.WHITE}BSSID: {bssid}"
            f"{Style.RESET_ALL} | {signal_color}Signal: {signal:>3}%"
            f"{Style.RESET_ALL} | {Fore.CYAN}Channel: {channel:<3}"
            f"{Style.RESET_ALL} | {security_color}Security: {security}"
            )
                
if __name__ == "__main__":
    scan_wifi_network() 
