import sqlite3
import time
from telethon import TelegramClient
from telethon import sync, events
from colorama import init, Fore, Back, Style
import re
import json

from colorama import init, Fore, Back, Style
init(autoreset=True)

def out_red(text):
    print(Style.BRIGHT + Fore.RED + str(text))
def out_blue(text):
    print(Style.BRIGHT + Fore.CYAN + str(text))
def out_green(text):
    print(Style.BRIGHT + Fore.GREEN + str(text))

db = sqlite3.connect('Account.db')
cur = db.cursor()

x = 1
summa = 0
bot_count = 12
available = 0

while(True):
    if x == (bot_count + 1):
        print('')
        out_green('===============================================')
        print("Всего добыто:")
        print('{:.8f}'.format(summa))
        print('')
        out_green('Доступно к выводу: ' + str(available))
        out_green('===============================================')
        break
    cur.execute(f"SELECT PHONE FROM Account WHERE ID = '{x}'")
    #time.sleep(0.4)
    Phone = str(cur.fetchone()[0])
    print("Входим в аккаунт: " + Phone)

    cur.execute(f"SELECT API_ID FROM Account WHERE ID = '{x}'")
    #time.sleep(0.4)
    api_id = str(cur.fetchone()[0])
    cur.execute(f"SELECT API_HASH FROM Account WHERE ID = '{x}'")
    #time.sleep(0.4)
    api_hash = str(cur.fetchone()[0])
    session = str("sessio/anon" + str(x))
    client = TelegramClient(session, api_id, api_hash)
    client.start()

    dlgs = client.get_dialogs()
    for dlg in dlgs:
        if dlg.title == 'LTC Click Bot':
            tegmo = dlg

    client.send_message('LTC Click Bot', "/balance")
    time.sleep(2)
    msgs = client.get_messages(tegmo, limit=1)

    for mes in msgs:
        str_a = str(mes.message)
        zz = str_a.replace('Available balance: ', '')
        qq = zz.replace(' LTC', '')
        waitin = float(qq)
        if waitin > 0.0003:
            out_green('{:.8f}'.format(waitin))
        else:
            print('{:.8f}'.format(waitin))

    summa = summa + waitin

    if waitin > 0.0003:
        available = available + waitin

    #print(m)
    client.disconnect()
    x = x + 1