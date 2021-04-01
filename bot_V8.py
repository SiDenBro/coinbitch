import urllib.request
import webbrowser
import requests
import hashlib
import sqlite3
import json
import time
import re
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from telethon.tl.functions.channels import JoinChannelRequest
from telethon import TelegramClient
from telethon import sync, events

from colorama import init, Fore, Back, Style
init(autoreset=True)

def out_red(text):
    print(Style.BRIGHT + Fore.RED + str(text))
def out_blue(text):
    print(Style.BRIGHT + Fore.CYAN + str(text))
def out_green(text):
    print(Style.BRIGHT + Fore.GREEN + str(text))

class RunChromeTests():
    def testMethod(self):
        selenium_url = "http://localhost:4444/wd/hub"
        caps = {'browserName': 'chrome'}
        driver = webdriver.Remote(command_executor=selenium_url, desired_capabilities=caps)
        driver.maximize_window()
        driver.get(url_rec)
        time.sleep(waitin + 10)
        driver.close()
        driver.quit()

FLAG = "webs"
# subs
# bots
# webs


# DataBase connect
db = sqlite3.connect('Account.db')
cur = db.cursor()

# Config
x = 1                       # Начинаем с первого аккаунта
bot_count = 12              # Количество аккаунтов / Верхний предел
bot_low_limit = 1           # Нижний предел предел

noWork_limit = 2            # Лимит отсутствия заданий
iterations_limit = 10       # Сколько заданий попытается сделать бот за одну проходку
badWorkRequest_limit = 3    # Сколько может быть исключений при подписке на аккаунт

out_green('===========================================')
print('Starting')
print('Bot count = ' + str(bot_count))
print('Task in iteration = ' + str(iterations_limit))
print('Task type = ' + str(str.upper(FLAG)))
print('Start with bot # ' + str(x))
out_green('===========================================')

# Прогоняем все аккаунты
while True:
    noWork = 0          # Счётчик отсутствия работы
    iterations = 0      # Счётчик проделанной работы
    badWorkRequest = 0
    if x == (bot_count + 1):    # Если отработал последний бот
        x = bot_low_limit                   # То запускаем первого бота
    out_green('\n===========================================')
    out_blue("Account queue # " + str(x))

    # Логиним нового бота
    try:
        cur.execute(f"SELECT PHONE FROM Account WHERE ID = '{x}'")
        time.sleep(0.4)
        Phone = str(cur.fetchone()[0])
        out_blue("Logging...: " + Phone)
        cur.execute(f"SELECT API_ID FROM Account WHERE ID = '{x}'")
        time.sleep(0.4)
        api_id = str(cur.fetchone()[0])
        cur.execute(f"SELECT API_HASH FROM Account WHERE ID = '{x}'")
        time.sleep(0.4)
        api_hash = str(cur.fetchone()[0])
        session = str("sessio/anon" + str(x))
        client = TelegramClient(session, api_id, api_hash)
        client.start()
    except Exception:
        out_red('Account connection failed')
        out_blue('Skipping account...')
        x = x + 1
        break

    # Среди диалогов находим диалог с ботом для заданий
    dialogs = client.get_dialogs()
    for dialog in dialogs:
        if dialog.title == 'LTC Click Bot':
            tegmo = dialog

    # ЗАРАБАТЫВАЕМ НА ПОДПИСКАХ --- Я считаю это итоговый вариант
    if FLAG == "subs":
        while True:
            # Текствовый отчёт о лимитах
            if True:
                if noWork != 0:
                    print("Task missing: " + str(noWork) + " times")
                if noWork == noWork_limit:
                    out_blue("Go to another account")
                    break
                if iterations != 0:
                    print("Iterations passed: " + str(iterations) + ("\n" if (badWorkRequest == 0) else ""))
                if badWorkRequest != 0:
                    print("Exception [Subscription]: " + str(badWorkRequest) + "\n")
                if iterations == iterations_limit:
                    out_blue("Task Limit ===> Go to another account")
                    break
                if badWorkRequest == badWorkRequest_limit:
                    out_blue("Exception [Subscription] Limit ===> Go to another account")
                    break

            client.send_message('LTC Click Bot', "📣 Join chats")
            time.sleep(2)

            msgs = client.get_messages(tegmo, limit=1)

            for mes in msgs:
                if re.search(r'After joining, press the', mes.message):
                    # Getting a link
                    try:
                        url_rec = mes.reply_markup.rows[0].buttons[0].url
                        out_green(str(url_rec))
                    except Exception:
                        out_red("Exception [Failed to get URL]")
                        iterations = iterations + 1
                        break

                    pagedata = str(requests.get(url_rec).text)
                    #time.sleep(5)
                    groupName = str(re.findall(r'<title>Telegram: Contact (.*?)</title>', pagedata))

                    if groupName != "[]":
                        groupName = groupName.replace("['", "")
                        groupName = groupName.replace("']", "")
                        groupNameNoDog = groupName.replace("@", "")
                        out_green(str(groupName))

                        # Subscribe
                        try:
                            client(JoinChannelRequest(groupName))
                        except Exception:
                            out_red("Exception [bad subscription]")
                            out_blue('Skipping task...')
                            try:
                                button_data = mes.reply_markup.rows[1].buttons[1].data
                                message_id = mes.id
                                from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                                resp = client(GetBotCallbackAnswerRequest(
                                    tegmo,
                                    message_id,
                                    data=button_data
                                ))
                                out_blue('Task skipped')
                            except Exception:
                                out_red('Task not skipped - Exception [bad skipping]')
                            badWorkRequest = badWorkRequest + 1
                            break

                        time.sleep(3)
                        # Нажимаем на проверку
                        print("Check for subscription")
                        try:
                            button_data = mes.reply_markup.rows[0].buttons[1].data
                            message_id = mes.id
                            from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                            resp = client(GetBotCallbackAnswerRequest(
                                tegmo,
                                message_id,
                                data=button_data
                            ))
                            time.sleep(2)
                            out_green("Check successful")
                        except Exception:
                            badWorkRequest = badWorkRequest + 1  
                            out_green("Exception - [Bad checking]") 
                            out_blue('Skipping task...')
                            try:
                                button_data = mes.reply_markup.rows[1].buttons[1].data
                                message_id = mes.id
                                from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                                resp = client(GetBotCallbackAnswerRequest(
                                    tegmo,
                                    message_id,
                                    data=button_data
                                ))
                                out_blue('Task skipped')
                            except Exception:
                                out_red('Task not skipped - Exception [bad skipping]')
                            badWorkRequest = badWorkRequest + 1
                            break

                        iterations = iterations + 1
                    else:
                        out_red("Exception - [Empty title]")
                        out_blue('Skipping task...')
                        try:
                            button_data = mes.reply_markup.rows[1].buttons[1].data
                            message_id = mes.id
                            from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
                            resp = client(GetBotCallbackAnswerRequest(
                                tegmo,
                                message_id,
                                data=button_data
                            ))
                            out_blue('Task skipped')
                        except Exception:
                            out_red('Task not skipped - Exception [Bad skipping]')

                elif re.search(r'Sorry, there are no new ads available', mes.message):
                    out_blue("Founded Sorry ===>  " + str(noWork + 1))
                    noWork = noWork + 1
                elif re.search(r'Sorry, that task is no longer valid', mes.message):
                    out_blue("Task is no longer available")
                else:
                    out_red('Task message not found')
                    badWorkRequest = badWorkRequest + 1
            time.sleep(16)

    # ЗАРАБАТЫВАЕМ НА СТАРТИНГЕ ЧУЖИХ БОТОВ
    if FLAG == "bots":
        lastBot = ""
        while True:
            # Текствовый отчёт о лимитах
            if True:
                if noWork != 0:
                    print("Task missing: " + str(noWork) + " times")
                if noWork == noWork_limit:
                    out_blue("Go to another account")
                    break
                if iterations != 0:
                    print("Iterations passed: " + str(iterations) + "\n")
                if badWorkRequest != 0:
                    print("Exception [Subscription]: " + str(badWorkRequest) + "\n")
                if iterations == iterations_limit:
                    out_blue("Go to another account")
                    break
                if badWorkRequest == badWorkRequest_limit:
                    out_blue("Exception [Subscription] Limit ===> Go to another account")
                    break

            client.send_message('LTC Click Bot', "🤖 Message bots")
            time.sleep(2)

            msgs = client.get_messages(tegmo, limit=1)

            for mes in msgs:
                if re.search(r'Forward a message to me from the bot to earn LTC', mes.message):
                    # Getting a link
                    try:
                        url_rec = mes.reply_markup.rows[0].buttons[0].url
                        out_green(str(url_rec))
                    except Exception:
                        out_red("Exception [Failed to get URL]")
                        iterations = iterations + 1
                        break

                    pagedata = str(requests.get(url_rec).text)
                    time.sleep(5)

                    botName = str(re.findall(r'<title>Telegram: Contact (.*?)</title>', pagedata))
                    if botName != "[]":
                        botName = botName.replace("['", "")
                        botName = botName.replace("']", "")
                        botNameNoDog = botName.replace("@", "")

                        if lastBot == botName:
                            out_blue('Maybe bot not worked')
                            out_blue('Skipping task...')
                            try:
                                button_data = mes.reply_markup.rows[1].buttons[1].data
                                message_id = mes.id
                                from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                                resp = client(GetBotCallbackAnswerRequest(
                                    tegmo,
                                    message_id,
                                    data=button_data
                                ))
                                out_blue('Task skipped')
                            except Exception:
                                out_red('Task not skipped - Exception [Bad skipping]')
                                badWorkRequest = badWorkRequest + 1
                        else:
                            lastBot = botName
                            out_green(str(botName))
                            # Communication with bots
                            try:
                                client.send_message(botName, '/start')
                                time.sleep(3)

                                messagesTask = client.get_messages(botNameNoDog)

                                for task in messagesTask:
                                    if task.message != '/start':
                                        client.forward_messages('@Litecoin_click_bot', messagesTask[0])
                                        time.sleep(2)
                                        out_green('Task completed')
                                        break

                                iterations = iterations + 1
                            # No communication with bots
                            except Exception:
                                out_red('No communication with bots')
                                out_blue('Skipping task...')
                                try:
                                    button_data = mes.reply_markup.rows[1].buttons[1].data
                                    message_id = mes.id
                                    from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                                    resp = client(GetBotCallbackAnswerRequest(
                                        tegmo,
                                        message_id,
                                        data=button_data
                                    ))
                                    out_blue('Task skipped')
                                except Exception:
                                    out_red('Task not skipped - Exception [Bad skipping]')
                                    badWorkRequest = badWorkRequest + 1
                                iterations = iterations + 1
                    else:
                        out_red("Exception - [Empty title]")
                        out_blue('Skipping task...')
                        iterations = iterations + 1
                        try:
                            button_data = mes.reply_markup.rows[1].buttons[1].data
                            message_id = mes.id
                            from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                            resp = client(GetBotCallbackAnswerRequest(
                                tegmo,
                                message_id,
                                data=button_data
                            ))
                            out_blue('Task skipped')
                        except Exception:
                            out_red('Task not skipped - Exception [Bad skipping]')
                            badWorkRequest = badWorkRequest + 1

                elif re.search(r'Sorry, there are no new ads available', mes.message):
                    out_blue("Founded Sorry ===>  " + str(noWork + 1))
                    noWork = noWork + 1
                elif re.search(r'Sorry, that task is no longer valid', mes.message):
                    out_blue("Task is no longer available")
                else:
                    out_red('Task message not found')
                    badWorkRequest = badWorkRequest + 1
            time.sleep(16)

    # ЗАРАБАТЫВАЕМ НА ЧЕКАНИИ САЙТОВ
    if FLAG == "webs":
        per10 = ""

        while True:
            # Текствовый отчёт о лимитах
            if True:
                if noWork != 0:
                    print("Task missing: " + str(noWork) + " times")
                if noWork == noWork_limit:
                    out_blue("Go to another account")
                    break
                if iterations != 0:
                    print("Iterations passed: " + str(iterations) + "\n")
                if badWorkRequest != 0:
                    print("Exception [Subscription]: " + str(badWorkRequest) + "\n")
                if iterations == iterations_limit:
                    out_blue("Go to another account")
                    break
                if badWorkRequest == badWorkRequest_limit:
                    out_blue("Exception [Subscription] Limit ===> Go to another account")
                    break

            client.send_message('LTC Click Bot', "🖥 Visit sites")
            time.sleep(2)

            msgs = client.get_messages(tegmo, limit=1)

            for mes in msgs:
                # It's shit
                if re.search(r'\bseconds to get your reward\b', mes.message):
                    out_green("Найдено reward")
                    str_a = str(mes.message)
                    zz = str_a.replace('You must stay on the site for', '')
                    qq = zz.replace('seconds to get your reward.', '')
                    waitin = int(qq)
                    print("Ждать придется: ", waitin)
                    client.send_message('LTC Click Bot', "/visit")
                    time.sleep(3)
                    msgs2 = client.get_messages(tegmo, limit=1)

                    for mes2 in msgs2:
                        button_data = mes2.reply_markup.rows[1].buttons[1].data
                        message_id = mes2.id
                        print("Перехожу по ссылке")
                        time.sleep(2)
                        url_rec = messages[0].reply_markup.rows[0].buttons[0].url
                        ch = RunChromeTests()
                        ch.testMethod()
                        time.sleep(6)
                        fp = urllib.request.urlopen(url_rec)
                        mybytes = fp.read()
                        mystr = mybytes.decode("utf8")
                        fp.close()
                        if re.search(r'\bSwitch to reCAPTCHA\b', mystr):
                            from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                            resp = client(GetBotCallbackAnswerRequest(
                                'LTC Click Bot',
                                message_id,
                                data=button_data
                            ))
                            time.sleep(2)
                            print("КАПЧА!")
                        else:
                            time.sleep(waitin)
                            time.sleep(2)

                # It's good job
                elif re.search(r'Press the "Visit website" button to earn LTC', mes.message):
                    try:
                        url_rec = mes.reply_markup.rows[0].buttons[0].url
                        out_green(url_rec)
                    except Exception:
                        out_red("Exception [Failed to get URL]")
                        badWorkRequest = badWorkRequest + 1
                        break

                    if per10 == url_rec:
                        out_blue("Link repeating")
                        out_blue('Skipping task...')
                        try:
                            button_data = mes.reply_markup.rows[1].buttons[1].data
                            message_id = mes.id
                            from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

                            resp = client(GetBotCallbackAnswerRequest(
                                tegmo,
                                message_id,
                                data=button_data
                            ))
                            out_blue('Task skipped')
                        except Exception:
                            out_red('Task not skipped - Exception [Bad skipping]')
                            badWorkRequest = badWorkRequest + 1
                    else:
                        data1 = requests.get(url_rec).json
                        print(data1)

                        out_green('Request sending....')
                        per10 = url_rec

                        time.sleep(3)
                        out_green('Task completed')
                        iterations = iterations + 1

                elif re.search(r'Sorry, there are no new ads available', mes.message):
                    out_blue("Founded Sorry ===>  " + str(noWork + 1))
                    noWork = noWork + 1
                elif re.search(r'Sorry, that task is no longer valid', mes.message):
                    out_blue("Task is no longer available")
                else:
                    out_red('Task message not found')
                    badWorkRequest = badWorkRequest + 1
            time.sleep(15)

    client.disconnect()
    x = x + 1