import os
import subprocess
import sys
from colorama import init, Fore, Back, Style
import time

init()

def console_picture():
    print(Style.BRIGHT + Fore.YELLOW)
    print("  _____          _                           _            ____            _   ")
    time.sleep(0.05)
    print(" |_   _|  _ __  (_)   __ _   _ __     __ _  | |   ___    | __ )    ___   | |_ ")
    time.sleep(0.05)
    print("   | |   | '__| | |  / _` | | '_ \   / _` | | |  / _ \   |  _ \   / _ \  | __|")
    time.sleep(0.05)
    print("   | |   | |    | | | (_| | | | | | | (_| | | | |  __/   | |_) | | (_) | | |_ ")
    time.sleep(0.05)
    print("   |_|   |_|    |_|  \__,_| |_| |_|  \__, | |_|  \___|   |____/   \___/   \__|")
    time.sleep(0.05)
    print("                                     |___/                                    ")
    time.sleep(0.05)
console_picture()
print("Нажми Enter чтобы запустить...")
input()

while (True):
    process = subprocess.Popen([sys.executable, "bot_V8.py"])
    process.wait()
